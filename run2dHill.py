#! /usr/bin/env python
# -*- coding: utf-8 -*-

# runs simpleFoam with k-epsilon closure for 2D geometry based on a reference case containing the appropriate dictionaries
# the bottom hill/valley/shape is given in function writeGroundShape.py
# run2dHill.py uses templates included in the case, and changes the boundary conditions and creates a mesh according 
# to specified arguments
# example call to function:
# run2dHill.py template        	target     r    x  Ls   L   x0  plotAll H (list of H) 
# run2dHill.py Bump2D 		Bump2D_win 1.04 20 1500 500 0.5 1 	2000

# where
# template 	- the case with the appropriate dictionaries, templates and boundary conditions   
# target	- the result case base name (will be target_$Hn$)	   
# r   		- expansion ratio of cell in the y direction (perpendicular to ground)
# x  		- first cell size - yp = x * z0 where yp is the middle of the first cell (see Martinez 2010)
# Ls  		- half length of CV in x direction
# L 		- half length of refined area in x direction (where cell width is x0)
# x0   		- cell width in refined area
# plotAll 	- flag for plotting compaison - by calling plot2dHill.py
# H		- height of domain

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
from numpy import *
from pylab import *
import matplotlib.pyplot as plt
import os,glob,subprocess
from matplotlib.backends.backend_pdf import PdfPages

#--------------------------------------------------------------------------------------
# reading arguments
#--------------------------------------------------------------------------------------

# TODO learn the try thingy - here it would help
n = len(sys.argv)

if n<9:
  print "Need		<TEMPLATE> 		\n\
		<TARGET>  			\n\
		<r> 				\n\
		<x as in y0 = 2 * x * z0>  \n\
		<Ls - total half length of domain > \n\
		<L - refined half length > 	\n\
		<x0 - horizontal grid spacing> 	\n\
		<plotAll>			\n\
		<Hn as in H = Hn*h where h is the hill height>"
  sys.exit(-1)

template0 = sys.argv[1]
target0  = target = sys.argv[2]
r        = float(sys.argv[3])
x        = float(sys.argv[4])
Ls       = float(sys.argv[5])
L        = float(sys.argv[6])
L1 = L/2 #upwind refined area smaller then downwind
x0       = float(sys.argv[7])
plotAll	 = int(sys.argv[8])

# case definitions - RUSHIL
z0 = 0.000157 	# [m]
ks = 19.58 * z0 # [m] Martinez 2011
h = 0.117    	# hill height
Utop = 4	# [m/s] Castro 96
us = 0.188	# [m/s] some say 0.178 (not Castro - for him us/Utop = 0.047 --> us = 0.188 
k = 0.4
Cmu = 0.09 	# Castro 96
funky = 1
Href = Htop = exp(Utop*k/us)*z0
k_infty = us**2/sqrt(Cmu)*0.01 # Catro 96

# case definitions Martinez2DBump
z0 = 0.005 	# [m]
ks = 19.58 * z0 # [m] Martinez 2011
h = 60    	# hill height
us = 0.5315	# [m/s] 
k = 0.4
Cmu = 0.03 	# Castro 96
x = 20
Ls = 1500	# [m]
H = Htop = Href = 2000	# [m]

# yp/ks = 0.02 = x/ks
funky = 0
plotMartinez = 1
hSample = 10

procnr = 2

for HNum in range(9,n):
	# looping Hn inputs
	H = float(sys.argv[HNum])
	HStr = str(sys.argv[HNum])
  	target = target0+HStr
  	print "H = "+HStr
	orig = SolutionDirectory(template0,
			  archive=None,
			  paraviewLink=False)
	#--------------------------------------------------------------------------------------
	# cloaning case
	#--------------------------------------------------------------------------------------
	work = orig.cloneCase(target)
	# copying experimental data
	subprocess.call("cp -r " + str(template0) + "/Martinez_Figure21a.csv " + str(target),shell=True)
	subprocess.call("cp -r " + str(template0) + "/Martinez_Figure21b.csv " + str(target),shell=True)
	subprocess.call("cp -r " + str(template0) + "/Martinez_Figure21c.csv " + str(target),shell=True)

	#--------------------------------------------------------------------------------------
	# creating mesh
	#--------------------------------------------------------------------------------------
	y0 =  2 * x * z0 # setting first cell according to Martinez 2011 p. 25
	ny = int(round(math.log(H/y0*(r-1)+1)/math.log(r)))    # number of cells in the y direction of the hill block
	Ry  = r**(ny-1.)
	print "Hill block: ny = " +str(ny) + " ,Ry = " + str(Ry) 
	nx = int(L/x0-1)
	rx = max(r,1.1)
	ns = int(round(math.log((Ls-L)/x0*(rx-1)+1)/math.log(rx)))    # number of cells in the y direction of the hill block
	Rx = rx**(ns-1)
	print "Side blocks: ns = " +str(ns) + " ,Rx = " + str(Rx) 
	# changing blockMeshDict - from template file
	bmName = path.join(work.constantDir(),"polyMesh/blockMeshDict")
	template = TemplateFile(bmName+"_3cell.template")
	template.writeToFile(bmName,{'H':H,'ny':ny,'Ry':Ry,'nx':nx,'L':L,'L1':L1,'Ls':Ls,'Rx':Rx,'Rx_one_over':1/Rx,'ns':ns})
	# writing ground shape (hill, or whatever you want - equation in function writeGroundShape.py)
	# sample file is changed as well - for sampling h=10 meters above ground
	import writeGroundShape
	sampleName = path.join(work.systemDir(),"sampleDict.template")
	writeGroundShape.main(bmName,H,L,sampleName,hSample)
	# changing Y line limits
	bmName = path.join(work.systemDir(),"sampleDict")
	template = TemplateFile(bmName + ".template")
	template.writeToFile(bmName,{'hillTopY':h,'maxY':500})
	
	# running blockMesh
	blockRun = BasicRunner(argv=["blockMesh",'-case',work.name],silent=True,server=False,logname="blockMesh")
	print "Running blockMesh"
	blockRun.start()
	if not blockRun.runOK(): error("there was an error with blockMesh")

	#--------------------------------------------------------------------------------------
	# changing inlet profile - - - - according to Martinez 2010
	#--------------------------------------------------------------------------------------
	# change inlet profile
	Uref = Utop = us/k*math.log(Href/z0)
 	print "Htop = " + str(Htop) + ", Utop = " + str(Utop)
	# calculating turbulentKE
	TKE = us*us/math.sqrt(Cmu)
	print "TKE = "+str(TKE)
	# 1: changing ABLConditions
	bmName = path.join(work.initialDir(),"include/ABLConditions")
	template = TemplateFile(bmName+".template")
	template.writeToFile(bmName,{'us':us,'Uref':Uref,'Href':Href,'z0':z0})
	# 2: changing initialConditions
	bmName = path.join(work.initialDir(),"include/initialConditions")
	template = TemplateFile(bmName+".template")
	template.writeToFile(bmName,{'TKE':TKE})
	
	if funky:	
		# 3: changing U (inserting variables into groovyBC for inlet profile)
		bmName = path.join(work.initialDir(),"U")
		template = TemplateFile(bmName + ".template")
 		template.writeToFile(bmName,{'us':us,'z0':z0,'K':k,'Utop':Utop})
		# 4: changing k (inserting variables into groovyBC for inlet profile)
		bmName = path.join(work.initialDir(),"k")
		template = TemplateFile(bmName + ".template")
	 	template.writeToFile(bmName,{'us':us,'z0':z0,'K':k,'Utop':Utop,'Cmu':Cmu})
		# 5: changing epsilon (inserting variables into groovyBC for inlet profile)
		bmName = path.join(work.initialDir(),"epsilon")
		template = TemplateFile(bmName + ".template")
	 	template.writeToFile(bmName,{'us':us,'z0':z0,'K':k,'Utop':Utop,'Cmu':Cmu})

	# 6: changing initial and boundary conditions for new z0
	# changing ks in nut, inside nutRoughWallFunction
	nutFile = ParsedParameterFile(path.join(work.initialDir(),"nut"))
	nutFile["boundaryField"]["ground"]["Ks"].setUniform(ks)
	nutFile.writeFile()
 
	#--------------------------------------------------------------------------------------
	# decomposing
	#--------------------------------------------------------------------------------------
	# removing U.template from 0/ directory
	subprocess.call("rm " + bmName + ".template ",shell=True)
 	print "Decomposing"
 	Decomposer(args=["--progress",work.name,procnr])
 	CaseReport(args=["--decomposition",work.name])


	#--------------------------------------------------------------------------------------
	# running
	#--------------------------------------------------------------------------------------
	machine = LAMMachine(nr=procnr)
	# run case
	PlotRunner(args=["--proc=%d"%procnr,"--with-all","--progress","simpleFoam","-case",work.name])
	#PlotRunner(args=["simpleFoam","-parallel","- proc =% d " % procnr, "-case",work.name])
	print "work.name = ", work.name
	Runner(args=["reconstructPar","-latestTime","-case",work.name])

	# sample results
	dirNameList = glob.glob(target + "*")
	dirNameList.sort()
	print "\nSampling the following cases:"
	print dirNameList
	for dirName in dirNameList:
 		# sampling
 		arg = " -case " + dirName + "/"
 		print arg
 		#subprocess.call("R"+ arg,shell=True) # calculating reynolds stress tensor
 		subprocess.call("sample -latestTime"+ arg,shell=True)

# plotting
if plotMartinez:
	import plotMartinez2DBump
	plotMartinez2DBump.main(target,hSample)
	plt.show()
elif plotAll:
	import plot2dHill
 	plot2dHill.main(target,"U phi k TI")
 	plt.show()



