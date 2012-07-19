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
import os,glob,subprocess, multiprocessing
from matplotlib.backends.backend_pdf import PdfPages
import pdb
b = pdb.set_trace

def run3dHillBase(template0, AR, z0, us, caseType):

	# loading other parameters from dictionary file
	inputDict = ParsedParameterFile("testZ0InfluenceDict")
	h		= inputDict["simParams"]["h"]
	yM 		= inputDict["simParams"]["yM"]
	# SHM parameters
	cell	= inputDict["SHMParams"]["cellSize"]["cell"] 
	Href = inputDict["SHMParams"]["domainSize"]["domZ"] 
	zz = inputDict["SHMParams"]["pointInDomain"]["zz"]
	# case definitions Martinez2DBump
	ks = 19.58 * z0 # [m] Martinez 2011
	k = inputDict["kEpsParams"]["k"]
	Cmu = inputDict["kEpsParams"]["Cmu"]	
	# yp/ks = 0.02 = x/ks
	hSample = inputDict["sampleParams"]["hSample"]
	procnr = multiprocessing.cpu_count()
	caseStr = "_z0_" + str(z0)
  	target = "runs/" + template0 + caseStr
  	x0, y0, phi = 	inputDict["SHMParams"]["centerOfDomain"]["x0"], inputDict["SHMParams"]["centerOfDomain"]["x0"], \
  					inputDict["SHMParams"]["flowOrigin"]["deg"]*pi/180
  	H = h
  	a = h*AR
	#--------------------------------------------------------------------------------------
	# cloaning case
	#--------------------------------------------------------------------------------------
	orig = 	SolutionDirectory(template0,
			archive=None,
			paraviewLink=False)
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
	template.writeToFile(bmName,{'us':us,'Uref':Uref,'Href':Href,'z0':z0,'xDirection':sin(phi),'yDirection':cos(phi)})
	# 2: changing initialConditions
	bmName = path.join(work.initialDir(),"include/initialConditions")
	template = TemplateFile(bmName+".template")
	template.writeToFile(bmName,{'TKE':TKE})
	# 3: changing initial and boundary conditions for new z0
	# changing ks in nut, inside nutRoughWallFunction
	nutFile = ParsedParameterFile(path.join(work.initialDir(),"nut"))
	nutFile["boundaryField"]["ground"]["Ks"].setUniform(ks)
	nutFile["boundaryField"]["terrain_.*"]["Ks"].setUniform(ks)
	nutFile.writeFile()
	
	#--------------------------------------------------------------------------------------
	# changing sample file
	#--------------------------------------------------------------------------------------
	# 2: changing initialConditions
	bmName = path.join(work.systemDir(),"sampleDict")
	template = TemplateFile(bmName+".template")
	template.writeToFile(bmName,{'hillTopY':h,'sampleHeightAbovePlain':50,'sampleHeightAboveHill':h+50,'inletX':h*AR*5*0.9}) 
	
	# if SHM - create mesh
	if caseType=="SHM":
	
		#--------------------------------------------------------------------------------------
		# creating blockMeshDict
		#--------------------------------------------------------------------------------------
		l, d = a*inputDict["SHMParams"]["domainSize"]["fX"], a*inputDict["SHMParams"]["domainSize"]["fY"]
		x1 = x0 - (l/2*sin(phi) + d/2*cos(phi))
		y1 = y0 - (l/2*cos(phi) - d/2*sin(phi))
		x2 = x0 - (l/2*sin(phi) - d/2*cos(phi))
		y2 = y0 - (l/2*cos(phi) + d/2*sin(phi))
		x3 = x0 + (l/2*sin(phi) + d/2*cos(phi))
		y3 = y0 + (l/2*cos(phi) - d/2*sin(phi))
		x4 = x0 + (l/2*sin(phi) - d/2*cos(phi))
		y4 = y0 + (l/2*cos(phi) + d/2*sin(phi))
		n = floor(d/cell)
		m = floor(l/cell)
		q = floor((Href+450)/cell) # -450 is the minimum of the blockMeshDict.template - since that is slightly lower then the lowest point on the planet

		bmName = path.join(work.constantDir(),"polyMesh/blockMeshDict")
		template = TemplateFile(bmName+".template")
		template.writeToFile(bmName,{'X0':x1,'X1':x2,'X2':x3,'X3':x4,'Y0':y1,'Y1':y2,'Y2':y3,'Y3':y4,'Z0':Href,'n':int(n),'m':int(m),'q':int(q)})
		
		#--------------------------------------------------------------------------------------
		# running blockMesh
		#--------------------------------------------------------------------------------------
		blockRun = BasicRunner(argv=["blockMesh",'-case',work.name],silent=True,server=False,logname="blockMesh")
		print "Running blockMesh"
		blockRun.start()
		if not blockRun.runOK(): error("there was an error with blockMesh")

		#--------------------------------------------------------------------------------------
		# running SHM
		#--------------------------------------------------------------------------------------
		print "calculating SHM parameters"
		# calculating refinement box positions
		l1, l2, h1, h2 = 2*a, 1.3*a, 4*H, 2*H # refinement rulls - Martinez 2011
		refBox1_minx, refBox1_miny, refBox1_minz = x0 + l1*(sin(phi)+cos(phi)), y0 - l1*(cos(phi)-sin(phi)), 0 #enlarging to take acount of the rotation angle
		refBox1_maxx, refBox1_maxy, refBox1_maxz = x0 - l1*(sin(phi)+cos(phi)), y0 + l1*(cos(phi)-sin(phi)), h1 #enlarging to take acount of the rotation angle
		refBox2_minx, refBox2_miny, refBox2_minz = x0 + l2*(sin(phi)+cos(phi)), y0 - l2*(cos(phi)-sin(phi)), 0 #enlarging to take acount of the rotation angle
		refBox2_maxx, refBox2_maxy, refBox2_maxz = x0 - l2*(sin(phi)+cos(phi)), y0 + l2*(cos(phi)-sin(phi)),h2 #enlarging to take acount of the rotation angle
		
		# changing cnappyHexMeshDict - with parsedParameterFile
		SHMDict = ParsedParameterFile(path.join(work.systemDir(),"snappyHexMeshDict"))
		SHMDict["geometry"]["refinementBox1"]["min"] = "("+str(refBox1_minx)+" "+str(refBox1_miny)+" "+str(refBox1_minz)+")"
		SHMDict["geometry"]["refinementBox1"]["max"] = "("+str(refBox1_maxx)+" "+str(refBox1_maxy)+" "+str(refBox1_maxz)+")"
		SHMDict["geometry"]["refinementBox2"]["min"] = "("+str(refBox2_minx)+" "+str(refBox2_miny)+" "+str(refBox2_minz)+")"
		SHMDict["geometry"]["refinementBox2"]["max"] = "("+str(refBox2_maxx)+" "+str(refBox2_maxy)+" "+str(refBox2_maxz)+")"
		SHMDict["castellatedMeshControls"]["locationInMesh"] = "("+str(x0)+" "+str(y0)+" "+str(zz)+")"
		levelRef = inputDict["SHMParams"]["cellSize"]["levelRef"]
		SHMDict["castellatedMeshControls"]["refinementSurfaces"]["terrain"]["level"] = "("+str(levelRef)+" "+str(levelRef)+")"
		L = inputDict["SHMParams"]["cellSize"]["layers"]
		SHMDict["addLayersControls"]["layers"]["terrain_solid"]["nSurfaceLayers"] = L
		r = inputDict["SHMParams"]["cellSize"]["r"]
		SHMDict["addLayersControls"]["expansionRatio"] = r
		# calculating finalLayerRatio for getting 
		zp_z0 = inputDict["SHMParams"]["cellSize"]["zp_z0"]
		firstLayerSize = 2*zp_z0*z0
		fLayerRatio = firstLayerSize*r**(L-1)*2**levelRef / cell
	
		SHMDict["addLayersControls"]["finalLayerThickness"] = fLayerRatio
		SHMDict.writeFile()
		"""
		# changing snappyHexMeshDict - with template file
		snapName = path.join(work.systemDir(),"snappyHexMeshDict")
		template = TemplateFile(snapName+".template")
		template.writeToFile(snapName,{	'refBox1_minx':refBox1_minx,'refBox1_miny':refBox1_miny,'refBox1_minz':refBox1_minz,
							'refBox1_maxx':refBox1_maxx,'refBox1_maxy':refBox1_maxy,'refBox1_maxz':refBox1_maxz,
							'refBox2_minx':refBox2_minx,'refBox2_miny':refBox2_miny,'refBox2_minz':refBox2_minz,
							'refBox2_maxx':refBox2_maxx,'refBox2_maxy':refBox2_maxy,'refBox2_maxz':refBox2_maxz,
							'locInMesh_x':x0,'locInMesh_y':y0,'locInMesh_z':zz})
		"""
		SHMrun = BasicRunner(argv=["snappyHexMesh",'-overwrite','-case',work.name],server=False,logname="SHM")
		print "Running SHM"
		SHMrun.start()
	
	
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


