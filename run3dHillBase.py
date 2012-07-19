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

import math, os
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
import pdb
b = pdb.set_trace

def run3dHillBase(template0, AR, z0, us, yM, h, caseType):

	# case definitions Martinez2DBump
	ks = 19.58 * z0 # [m] Martinez 2011
	k = 0.4
	Cmu = 0.03 	# Castro 96
	#TODO read this from case blockMeshDict or actual mesh?
	Href = 4000

	# yp/ks = 0.02 = x/ks
	funky = 0
	plotMartinez = 1
	hSample = 10
	fac = 10 # currecting calculation of number of cells and Rx factor to get a smooth transition 
		# from the inner refined cell and the outer less refined cells of the blockMesh Mesh
	procnr = 8

	caseStr = "_z0_" + str(z0)
  	
  	target = "runs/" + template0 + caseStr

	orig = SolutionDirectory(template0,
			  archive=None,
			  paraviewLink=False)
	#--------------------------------------------------------------------------------------
	# cloaning case
	#--------------------------------------------------------------------------------------
	work = orig.cloneCase(target)
				  
	#--------------------------------------------------------------------------------------
	# changing inlet profile - - - - according to Martinez 2010
	#--------------------------------------------------------------------------------------
	# change inlet profile
	Uref = Utop = us/k*math.log(Href/z0)
	# calculating turbulentKE
	TKE = us*us/math.sqrt(Cmu)
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
	# changing sample file
	#--------------------------------------------------------------------------------------
	# 2: changing initialConditions
	bmName = path.join(work.systemDir(),"sampleDict")
	template = TemplateFile(bmName+".template")
	template.writeToFile(bmName,{'hillTopY':h,'sampleHeightAbovePlain':50,'sampleHeightAboveHill':h+50,'inletX':h*AR*5*0.9}) 
	
	# mapping fields - From earlier result if exists
	if caseType == "mapFields":
		#finding the most converged run. assuming the "crude" run had the same dirName with "Crude" attached
  		setName =  glob.glob(target + 'Crude/sets/*')
  		lastRun = range(len(setName))
		for num in range(len(setName)):
			lastRun[num] = int(setName[num][setName[num].rfind("/")+1:])
  		sourceTimeArg = str(max(lastRun))
		mapRun = BasicRunner(argv=['mapFields -consistent -sourceTime ' + sourceTimeArg +
			 ' -case ' + work.name + ' ' + target + "Crude"],silent=True,server=False,logname='mapLog')
		mapRun.start()
		
	# parallel rule
	#print "Mesh has " + str(cells) + " cells"
	#if cells>100000: parallel=1
	#else: parallel=0
	parallel = 1
	if parallel:
		#--------------------------------------------------------------------------------------
		# decomposing
		#--------------------------------------------------------------------------------------
		# removing U.template from 0/ directory
		subprocess.call("rm " + bmName + ".template ",shell=True)
		arg = " -case " + work.name
	 	decomposeRun = BasicRunner(argv=["decomposePar -force" + arg],silent=True,server=False,logname="decompose")
		decomposeRun.start()


		#--------------------------------------------------------------------------------------
		# running
		#--------------------------------------------------------------------------------------
		machine = LAMMachine(nr=procnr)
		# run case
		PlotRunner(args=["--proc=%d"%procnr,"--progress","--no-continuity","--hardcopy", "--non-persist", "simpleFoam","-case",work.name])

		#--------------------------------------------------------------------------------------
		# reconstruct
		#-------------------------------------------------------------------------
		reconstructRun = BasicRunner(argv=["reconstructPar -latestTime" + arg],silent=True,server=False,logname="reconstructLog")
		reconstructRun.start()
	else:
		
		#--------------------------------------------------------------------------------------
		# running
		#--------------------------------------------------------------------------------------
		PlotRunner(args=["--progress","simpleFoam","-case",work.name])

	# sample results
	dirNameList = glob.glob(target + "*")
	dirNameList.sort()
	for dirName in dirNameList:
 		# sampling
 		arg = " -case " + dirName + "/"
 		sampleRun = BasicRunner(argv=["sample -latestTime" + arg],silent=True,server=False,logname="sampleLog")
		sampleRun.start()
 	#finding the most converged run.
  	setName =  glob.glob(dirName + '/sets/*')
  	lastRun = range(len(setName))
	for num in range(len(setName)):
		lastRun[num] = int(setName[num][setName[num].rfind("/")+1:])
  	m = max(lastRun)
  	p = lastRun.index(m)
	data_y = genfromtxt(setName[p] + '/line_y_U.xy',delimiter=' ')
  	y, Ux_y, Uy_y  = data_y[:,0], data_y[:,1], data_y[:,2] 
	if AR<1000: 	# if terrain isn't flat
		y = y-h # normalizing data to height of hill-top above ground

	return y,Ux_y,Uy_y


