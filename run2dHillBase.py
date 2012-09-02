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

def run2dHillBase(template0, target0, hillName, AR, r, x, Ls, L, L1, H, x0, z0, us, yM, h, caseType):

	# case definitions Martinez2DBump
	ks = 19.58 * z0 # [m] Martinez 2011
	k = 0.4
	Cmu = 0.03 	# Castro 96
	Htop = Href = H	# [m]

	# yp/ks = 0.02 = x/ks
	funky = 0
	plotMartinez = 1
	hSample = 10
	fac = 10 # currecting calculation of number of cells and Rx factor to get a smooth transition 
		# from the inner refined cell and the outer less refined cells of the blockMesh Mesh
	procnr = 8

	caseStr = "_AR_" + str(AR) + "_z0_" + str(z0)
	if caseType=="Crude": caseStr = caseStr + "Crude"
  	target = target0+caseStr
	orig = SolutionDirectory(template0,
			  archive=None,
			  paraviewLink=False)
	#--------------------------------------------------------------------------------------
	# cloaning case
	#--------------------------------------------------------------------------------------
	work = orig.cloneCase(target)

	#--------------------------------------------------------------------------------------
	# creating mesh
	#--------------------------------------------------------------------------------------
	y0 =  2 * x * z0 # setting first cell according to Martinez 2011 p. 25
	ny = int(round(math.log(H/y0*(r-1)+1)/math.log(r)))    # number of cells in the y direction of the hill block
	Ry  = r**(ny-1.)
	nx = int(L/x0-1)
	rx = max(r,1.1)
	ns = int(round(math.log((Ls-L)/x0*(rx-1)/rx**fac+1)/math.log(rx)))    # number of cells in the x direction of the hill block
	Rx = rx**(ns-1)
	# changing blockMeshDict - from template file
	if AR==1000: # if flat terrain
		bmName = path.join(work.constantDir(),"polyMesh/blockMeshDict")
		template = TemplateFile(bmName+"_flat_3cell.template")
	else:
		bmName = path.join(work.constantDir(),"polyMesh/blockMeshDict")
		template = TemplateFile(bmName+"_3cell.template")
	template.writeToFile(bmName,{'H':H,'ny':ny,'Ry':Ry,'nx':nx,'L':L,'L1':L1,'Ls':Ls,'Rx':Rx,'Rx_one_over':1/Rx,'ns':ns})
	# writing ground shape (hill, or whatever you want - equation in function writeGroundShape.py)
	# sample file is changed as well - for sampling h=10 meters above ground
	import write2dShape
	sampleName = path.join(work.systemDir(),"sampleDict.template")
	write2dShape.main(bmName,H,L,sampleName,hSample,hillName,AR)
	# changing Y line limits
	bmName = path.join(work.systemDir(),"sampleDict")
	template = TemplateFile(bmName + ".template")
	if AR==1000: # if flat terrain
		template.writeToFile(bmName,{'hillTopY':0,'maxY':yM*10})
	else:
		template.writeToFile(bmName,{'hillTopY':h,'maxY':yM*10+h})

	# running blockMesh
	blockRun = BasicRunner(argv=["blockMesh",'-case',work.name],silent=True,server=False,logname="blockMesh")
	blockRun.start()
	if not blockRun.runOK(): error("there was an error with blockMesh")

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
	
	# 7: changing convergence criterion for Crude runs
	if caseType == "Crude":	
		fvSolutionFile = ParsedParameterFile(path.join(work.systemDir(),"fvSolution"))
		fvSolutionFile["SIMPLE"]["residualControl"]["p"] = 1e-4
		fvSolutionFile["SIMPLE"]["residualControl"]["U"] = 1e-4
		fvSolutionFile.writeFile()
 	
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
	cells = nx * (ny+2*ns)
	print "Mesh has " + str(cells) + " cells"
	if cells>20000: parallel=1
	else: parallel=0

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
		PlotRunner(args=["--proc=%d"%procnr,"--progress","simpleFoam","-case",work.name])

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


