#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, math, os
from os import path
from PyFoam.RunDictionary.SolutionDirectory 	import SolutionDirectory
from PyFoam.Basics.TemplateFile 		import TemplateFile
from PyFoam.RunDictionary.ParsedParameterFile 	import ParsedParameterFile
from PyFoam.Basics.DataStructures 		import Vector
from PyFoam.Execution.BasicRunner 		import BasicRunner
from PyFoam.Applications.PlotRunner 		import PlotRunner
from PyFoam.Applications.Runner 		import Runner
from PyFoam.Applications.Decomposer 		import Decomposer
from PyFoam.Applications.CaseReport		import CaseReport
from PyFoam.Execution.ParallelExecution		import LAMMachine
from PyFoam.Applications.PotentialRunner	import PotentialRunner

import plot_z0

# reading arguments
n = len(sys.argv)
if n<4:
  print "Need <TEMPLATE> <TARGET> <withBlock> <Z0>"
  sys.exit(-1)
template = sys.argv[1]
orig = SolutionDirectory(template,
			  archive=None,
			  paraviewLink=False)
target0 = sys.argv[2]
withBlock = float(sys.argv[3])
#z0 = range(n-3)
for zNum in range(4,n):
  # looping z0 inputs
  z0 = float(sys.argv[zNum])
  z0Str = str(sys.argv[zNum])
  target = target0+z0Str
  print "z0 = "+z0Str
  
  # calculating z0 derived parameters
  # calculating ks according to Martinez 2011
  ks = 19.58 * z0
  print "ks = "+str(ks)
  # calculating ABLconditions - Ustar=$US according to logarithmic law
  k = 0.4
  Href = 700
  Uref = 17.4
  us = (Uref*k)/math.log((Href/z0));
  print "us = "+str(us)
  # calculating turbulentKE
  Cmu = 0.03
  TKE = us*us/math.sqrt(Cmu)
  print "TKE = "+str(TKE)
  
  # cloaning case
  work = orig.cloneCase(target)
  
  # changing initial and boundary conditions for new z0
  # changing ks in nut, inside nutRoughWallFunction
  nutFile = ParsedParameterFile(path.join(work.initialDir(),"nut"))
  nutFile["boundaryField"]["ground"]["Ks"].setUniform(ks)
  nutFile.writeFile()
  # changing ABLconditions
  bmName = path.join(work.initialDir(),"include/ABLconditions")
  template = TemplateFile(bmName+".template")
  template.writeToFile(bmName,{'z0':z0,'us':us})
  # changing initialConditions
  bmName = path.join(work.initialDir(),"include/initialConditions")
  template = TemplateFile(bmName+".template")
  template.writeToFile(bmName,{'TKE':TKE})
  
  # run the new case
  # creating mesh
  if withBlock==1:
    blockRun = BasicRunner(argv=["blockMesh",'-case',work.name],silent=True,server=False,logname="blocky")
    print "Running blockMesh"
    blockRun.start()
    if not blockRun.runOK(): error("there was an error with blockMesh")
  # decomposing
  print "Decomposing"
  Decomposer(args=["--progress",work.name,2])
  CaseReport(args=["--decomposition",work.name])
  # running
  machine = LAMMachine(nr=2)
  
  # laminar case for better first guess (rarely converges for 2D case with simpleFoam)
  print "running laminar case"
  turb = ParsedParameterFile(path.join(work.name,'constant/RASProperties'))
  turb["turbulence"]="off"
  turb.writeFile()
  dic = ParsedParameterFile(path.join(work.name,'system/controlDict'))
  dic["stopAt"] = "endTime"
  dic["endTime"] = 750
  dic.writeFile()
  PlotRunner(args=["--proc=2","simpleFoam","-case",work.name])
  # turbulent turned on
  print "turning turbulence on"
  turb["turbulence"]="on"
  turb.writeFile()
  dic["endTime"] = 4000
  dic.writeFile()
  PlotRunner(args=["--proc=2","simpleFoam","-case",work.name])
  # if it hasn't converged in 4000 steps - just use the result you have.
  # post processing
  Runner(args=["reconstructPar","-case",work.name])

# sampling (assuming sampleDict is edited seperately)
os.system("sample")
# plotting
plot_z0.main(template)

