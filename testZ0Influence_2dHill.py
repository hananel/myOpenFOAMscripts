#! /usr/bin/env python
# -*- coding: utf-8 -*-

# testZ0Influence_2dHill.py tests the effect that choosing z0 based on satelite image has on the calculated wind speed with OpenFOAM SimpleFOAM simulation
# This is done in the following steps:
# input: a. ground shape (or shapes - should be parameterized)
#	 b. measurement at 1 location (say 10 meter above hill center)
#	 c. z0 assumption
# 1. Producing a mesh
#    A blockMesh 2d volume mesh with a surface in the shape of a ideal hill (or hill series) is created
# 2. using z0 assumption, guessing ustar, running, comparing result with simulation, and changing ustar until convergence
# 3. sampling line above comparison point for the velocity at 2*M and 4/3*yM
# 4. running with z0+deltaz0 - according to davenport scale and assuming an error of one row in the table - and repeating steps 2 and 3
# 5. LATER repeating steps 1-4 for different geometry (say - hill aspect ratio) and delta z0 and producing a "contour map") 
#
# example call to function:
# testZ0Influence_2dHill.py template        	target  xM yM UM z0 AR
# testZ0Influence_2dHill.py 2DBumpTemplate 	Bump2D_AR_ 0 10 5 0.01 3

# where
# template 	- the case with the appropriate dictionaries, templates and boundary conditions   
# target	- the result case base name (will be target_$Hn$)	   
# x0
# y0
# U0
# z0
# AR		- hill aspect ratio (1000 == flat)
import sys, math, os, shutil
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
import Davenport

#--------------------------------------------------------------------------------------
# reading arguments
#--------------------------------------------------------------------------------------

# TODO learn the try thingy - here it would help
n = len(sys.argv)

if n<6:
  print "Need	<TEMPLATE> 		\n\
		<TARGET>  		\n\
		<>			\n\
		<>"
  sys.exit(-1)

template0 	= sys.argv[1]
target0  	= target = sys.argv[2]
xM 		= float(sys.argv[3])
yM 		= float(sys.argv[4])
UM 		= float(sys.argv[5])
z0 		= float(Davenport.Davenport(float(sys.argv[6]),0))

r        = 1.2
x        = 20
Ls       = 1000
L        = 500
L1 = L/2 #upwind refined area smaller then downwind
x0       = 20


# case definitions MartinezBump2D
hillName = "MartinezBump2D"
ks = 19.58 * z0 # [m] Martinez 2011
h = 60    	# hill height
us = 0.5315	# [m/s] 
k = 0.4
Cmu = 0.03 	# Castro 96
x = 20
H = Htop = Href = 1000	# [m]

# yp/ks = 0.02 = x/ks
funky = 0
plotMartinez = 1
hSample = 10
epsilon = 0.01
procnr = 8

for ARnum in range(7,n):

	# looping Hn inputs
	AR = float(sys.argv[ARnum])
	ARStr = str(sys.argv[ARnum])
  	target = target0+ARStr
	if AR==1000:
		print "flat terrain"
	else:
  		print "AR = "+ARStr
	orig = SolutionDirectory(template0,
			  archive=None,
			  paraviewLink=False)

	# erasing result folders
	subprocess.call("rm -R iteration* ",shell=True)
	subprocess.call("rm -R z0* ",shell=True)
	#shutil.rmtree("./iteration*")
	#shutil.rmtree("z0*")

	#--------------------------------------------------------------------------------------
	# cloaning case
	#--------------------------------------------------------------------------------------
	work = orig.cloneCase(target)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # #  		1	 	# # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

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
	template.writeToFile(bmName,{'hillTopY':h,'maxY':500})
	
	# running blockMesh
	blockRun = BasicRunner(argv=["blockMesh",'-case',work.name],silent=True,server=False,logname="blockMesh")
	print "Running blockMesh"
	blockRun.start()
	if not blockRun.runOK(): error("there was an error with blockMesh")
	
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # #  		2	 	# # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	# looping over us until convergence with measurements 
	notConverged = 1
	iteration = 1
	while notConverged:
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
		arg = " -case " + work.name
 		decomposeRun = BasicRunner(argv=["decomposePar -force" + arg],silent=True,server=False,logname="decompose")
		decomposeRun.start()		
		# subprocess.call("decomposePar -force " + arg,shell=True)
 		#Decomposer(args=["--progress",work.name,procnr])
 		#CaseReport(args=["--decomposition",work.name])


		#--------------------------------------------------------------------------------------
		# running
		#--------------------------------------------------------------------------------------
		machine = LAMMachine(nr=procnr)
		# run case
		PlotRunner(args=["--proc=%d"%procnr,"--progress","simpleFoam","-case",work.name])
		#PlotRunner(args=["simpleFoam","-parallel","- proc =% d " % procnr, "-case",work.name])
		print "work.name = ", work.name
		reconstructRun = BasicRunner(argv=["reconstructPar -latestTime" + arg],silent=True,server=False,logname="reconstructLog")
		reconstructRun.start()
		#Runner(args=["reconstructPar","-latestTime","-case",work.name],silent=True)
	
		# sample results
		dirNameList = glob.glob(target + "*")
		dirNameList.sort()
		print "\nSampling the following cases:"
		print dirNameList
		for dirName in dirNameList:
 			# sampling
 			arg = " -case " + dirName + "/"
 			print arg
 			sampleRun = BasicRunner(argv=["sample -latestTime" + arg],silent=True,server=False,logname="sampleLog")
			sampleRun.start()
 			#subprocess.call("sample -latestTime"+ arg,shell=True,silent=True)
		
		# checking convergence
		# finding the most converged run.
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
		UxSimulation = interp(yM,y,Ux_y)
		err = (UM-UxSimulation)/UM
		notConverged = abs(err)>epsilon
		
		print "UM = " + str(UM) + " ,UxSimulation = " + str(UxSimulation) + " ,error is " + str(err)
		# changing us
		relax = 1
		us = us/(1-err)*relax
		print "us = " + str(us)
		
		# deleting last sample results
		if notConverged :
			print "mv " + str(target) + "/sets/. iteration_" + str(iteration) + "_set"
			shutil.copytree(str(target) + "/sets/.", "iteration_" + str(iteration) + "_set")
			shutil.rmtree(str(target) + "/sets/")
		else :
			#subprocess.call("mv " + str(target) + "/sets/* z0_set" )
			print "mv " + str(target) + "/sets/. z0_set"
			shutil.copytree(str(target) + "/sets/.", "z0_set")
			shutil.rmtree(str(target) + "/sets/")
		# this file keeps getting erased in the cloaning process... so i just copy it from the original template directory
		subprocess.call("cp " + str(template0) + "/0/include/initialConditions.template " + str(target) + "/0/include/",shell=True)

		iteration = iteration + 1
	
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # #  		3	 	# # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	# sampling prediction of wind speed at 4/3*yM and 2*yM
	U43yM = interp(yM*4/3,y,Ux_y)
	U2yM = interp(yM*2,y,Ux_y)
	print "U43yM = " + str(U43yM) + " m/s"
	print "U2yM = " + str(U2yM) + " m/s"

	# output
	plt.figure(100)
	plt.plot(Ux_y,y,'k') 
	
	# PAUSE
	raw_input("press enter to continue")

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # #  		4	 	# # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	
	# running at z0 one scale higher in the Davenport scale
	z0Orig = z0
	z0 = Davenport.Davenport(z0Orig,1)
	print "changes z0 to " + str(z0) + " [m] was " + str(z0Orig) + " [m]"
	#--------------------------------------------------------------------------------------
	# changing inlet profile - and repeating the convergence
	#--------------------------------------------------------------------------------------
	# change inlet profile
	Uref = Utop = us/k*math.log(Href/z0)
 	print "Htop = " + str(Htop) + ", Utop = " + str(Utop)
	
	# 1: changing ABLConditions
	bmName = path.join(work.initialDir(),"include/ABLConditions")
	template = TemplateFile(bmName+".template")
	template.writeToFile(bmName,{'us':us,'Uref':Uref,'Href':Href,'z0':z0})
	
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
	ks = 19.58 * z0 # [m] Martinez 2011
	nutFile = ParsedParameterFile(path.join(work.initialDir(),"nut"))
	nutFile["boundaryField"]["ground"]["Ks"].setUniform(ks)
	nutFile.writeFile()
 
	#--------------------------------------------------------------------------------------
	# decomposing
	#--------------------------------------------------------------------------------------
	# removing U.template from 0/ directory
	subprocess.call("rm " + bmName + ".template ",shell=True)
 	print "Decomposing"
	arg = " -case " + work.name
 	decomposeRun = BasicRunner(argv=["decomposePar -force" + arg],silent=True,server=False,logname="decompose")
	decomposeRun.start()
	#subprocess.call("decomposePar -force " + arg,shell=True)

	#--------------------------------------------------------------------------------------
	# running
	#--------------------------------------------------------------------------------------
	machine = LAMMachine(nr=procnr)
	# run case
	PlotRunner(args=["--proc=%d"%procnr,"--progress","simpleFoam","-case",work.name])
	print "work.name = ", work.name
	reconstructRun = BasicRunner(argv=["reconstructPar -latestTime" + arg],silent=True,server=False,logname="reconstructLog")
	reconstructRun.start()
	#Runner(args=["reconstructPar","-latestTime","-case",work.name],silent=True)

	# sample results
	dirNameList = glob.glob(target + "*")
	dirNameList.sort()
	print "\nSampling the following cases:"
	print dirNameList
	for dirName in dirNameList:
		# sampling
		arg = " -case " + dirName + "/"
		print arg
		sampleRun = BasicRunner(argv=["sample -latestTime" + arg],silent=True,server=False,logname="sampleLog")
		sampleRun.start()
		#subprocess.call("sample -latestTime"+ arg,shell=True)
	
	# checking convergence
	# finding the most converged run.
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
	# sampling prediction of wind speed at 4/3*yM and 2*yM
	
	U43y_plus = interp(yM*4/3,y,Ux_y)
	U2y_plus = interp(yM*2,y,Ux_y)
	print "U43y +1 Davenport = " + str(U43y_plus) + " m/s"
	print "U2y +1 Davenport = " + str(U2y_plus) + " m/s"
	
	# moving set results 
	print "mv " + str(target) + "/sets/. z0_plus_set"
	shutil.copytree(str(target) + "/sets/.", "z0_plus_set")
	shutil.rmtree(str(target) + "/sets/")
	# output
	plt.figure(100)
	plt.plot(Ux_y,y,'r') 

# printing 

# plotting

#import plotZ0Influence
#plotZ0Influence.main(target,hSample)
plt.show()

def Davenport(z0, d):
	dav = np.array([0.0002, 0.005, 0.03, 0.1, 0.25, 0.5, 1, 2])
	if d > 0:
		sign = 1
	elif d < 0:
		sign = -1
	elif d == 0:
		sign=0
	else :
		print "insert a number for direction"
	print dav[dav.searchsorted(z0)+sign]
	return dav[dav.searchsorted(z0)+sign]



