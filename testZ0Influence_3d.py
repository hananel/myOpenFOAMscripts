#! /usr/bin/env python
# -*- coding: utf-8 -*-

# testZ0Influence_3d.py tests the effect that choosing z0 based on satelite image has on the calculated wind speed with OpenFOAM SimpleFOAM simulation
# This is done in the following steps:
# input: a. cases (3D) with ready meshes
#	 b. measurement at 1 location (say 10 meter above hill center)
#	 c. z0 assumption
# 1. Reading a mesh
# 2. using z0 assumption, guessing ustar, running, comparing result with simulation, and changing ustar until convergence
# 3. sampling line above comparison point for the velocity at 2*M and 4/3*yM
# 4a. running with z0+deltaz0 - according to davenport scale and assuming an error of one row in the table - and repeating steps 2 and 3
# 4b. same as 4a for Davenport scale one below
# 5. repeating steps 1-4 for different directories and delta z0 and producing a "contour map") 
#
# example call to function:
# testZ0Influence_3d.py template h xM yM UM z0 cell
# testZ0Influence_3d.py Martinez3D 200 0 20 5 0.03 100

# where
# h  - height of hill
# xM - x location of measurement
# yM - y location of measurement
# UM - velocity at xM,yM
# z0 - roughness length (same for entire area)
# cell - length of initial blockMesh cell

import sys, math, os, shutil, subprocess
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
from Davenport import Davenport
from run3dHillBase import run3dHillBase
from hilite import hilite
import pdb
b = pdb.set_trace

subprocess.call("killall gnuplot_x11",shell=True)
subprocess.call("clear",shell=True)

# TODO learn the try thingy - here it would help
n = len(sys.argv)

if n<1:
  print "Need <template> \n" #<h> <xM> <yM> <UM> <z0> <cell>\n"
  sys.exit(-1)

template= sys.argv[1]
template0 = template

# reading input dictionary - always named as below and resides in the current directory
inputDict = ParsedParameterFile("testZ0InfluenceDict")
h		= inputDict["simParams"]["h"]
xM 		= inputDict["simParams"]["xM"]
yM 		= inputDict["simParams"]["yM"]
UM 		= inputDict["simParams"]["UM"]
z0 		= Davenport(inputDict["simParams"]["z0"],0)
cell	= inputDict["SHMParams"]["cellSize"]["cell"] 

# TODO read this from file name
# h 	 =
k 	 = inputDict["kEpsParams"]["k"]	# von Karman constant

epsilon  = 0.001
caseType = inputDict["simParams"]["caseType"]

# logging
import logging
logger = logging.getLogger('testZ0Influence_3d')
hdlr = logging.FileHandler('testZ0Influence_3d.log')
sth = logging.StreamHandler()
sth.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.addHandler(sth)
logger.setLevel(logging.DEBUG)
logger.info('3D z0 influence log file')

# reading directory files (only running on existing directory cases)
# sample results
dirNameList = glob.glob(template + "*")
dirNameList.sort()

# outer loop - over directories
lenAR = len(dirNameList)
U43y = U2y = U43y_plus = U2y_plus = U43y_minus = U2y_minus = ARvec = zeros(lenAR,float)
logger.info(dirNameList)
subprocess.call("mkdir -p runs",shell=True)
for counter, dirName in enumerate(dirNameList):
	target0 = dirName
	
	# finding AR from dirname
	AR = float(dirName[dirName.rfind("AR_")+3:])
	logger.info("----------------------------------")

	logger.info("AR = " + str(AR))
	ARvec[counter] = AR

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # #  	      1, 2	 	# # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	# looping over us until convergence with measurements - using Crude mesh
	notConverged = 1
	# initial guess - according to flat terrain
	fac = 1 # /math.log(AR) # should be an intelegent function of hill AR
	us = UM*k/math.log(yM/z0)*fac
	logger.info("z0 = " + str(z0))
	logger.info("us = " + str((100*us//1)*0.01))
	while notConverged:
		y,Ux_y,Uy_y = run3dHillBase(template0, AR, z0, us,caseType)
		# checking convergence
		UxSimulation = interp(yM,y,Ux_y)
		err = (UM-UxSimulation)/UM
		notConverged = abs(err)>epsilon	
		logger.info("UM = " +  str((100*UM//1)*0.01) + " ,UxSimulation = " + 
				str((100*UxSimulation//1)*0.01) + " ,error is " + str(-err*100//1) + "%")
		# changing us
		us = us/(1-err)
		logger.info("us = " +  str((100*us//1)*0.01))
		logger.info("blind correction")
		Ux_y, Uy_y = Ux_y/(1-err), Uy_y/(1-err)
		notConverged = 0

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # #  		3	 	# # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	
	# saving results in matrix
	if counter==0:
		ymat = Ux_ymat = Uy_ymat = zeros([len(y),lenAR],float)
		ymat[:,counter] , Ux_ymat[:,counter] , Uy_ymat[:,counter] = y, Ux_y, Uy_y
	else:
		ymat[:,counter] , Ux_ymat[:,counter] , Uy_ymat[:,counter] = y, Ux_y, Uy_y

	# output
	fig1 = plt.figure(100)
	plt.plot(counter*10 + Ux_y,y,'k')
	plt.xlabel('U [m/s]')
	plt.ylabel('y [m]')

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # #  		4a	 	# # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	# running at z0 one scale higher in the Davenport scale
	z0Orig = z0
	z0 = Davenport(z0Orig,1)
	z0_plus = z0
	logger.info("----------------------------------")
	logger.info("changes z0 to " + str(z0) + " [m]")
	# looping over us until convergence with measurements 
	notConverged = 1
	# initial guess - according to flat terrain
	us = UM*k/math.log(yM/z0)

	logger.info("us = " + str((100*us//1)*0.01))
	while notConverged:
		y_plus,Ux_y_plus,Uy_y_plus = run3dHillBase(template0, AR, z0, us, caseType)
		# checking convergence
		UxSimulation = interp(yM,y_plus,Ux_y_plus)
		err = (UM-UxSimulation)/UM
		notConverged = abs(err)>epsilon	
		logger.info("UM = " +  str((100*UM//1)*0.01) + " ,UxSimulation = " + 
				str((100*UxSimulation//1)*0.01) + " ,error is " + str(-err*100//1) + "%")
		# changing us
		us = us/(1-err)
		logger.info("us = " +  str((100*us//1)*0.01))
		logger.info("blind correction")
		Ux_y, Uy_y = Ux_y/(1-err), Uy_y/(1-err)
		notConverged = 0
		
	# saving results in matrix
	if counter==0:
		ymat_plus = Ux_ymat_plus = Uy_ymat_plus = zeros([len(y),lenAR],float)
		ymat_plus[:,counter] , Ux_ymat_plus[:,counter] , Uy_ymat_plus[:,counter] = y_plus, Ux_y_plus, Uy_y_plus
	else:
		ymat_plus[:,counter] , Ux_ymat_plus[:,counter] , Uy_ymat_plus[:,counter] = y_plus, Ux_y_plus, Uy_y_plus

	# output
	plt.figure(100)
	plt.plot(counter*10 + Ux_y_plus,y_plus,'b')

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # #  		4b	 	# # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	# running at z0 one scale lowera in the Davenport scale
	z0 = Davenport(z0Orig,-1)
	z0_minus = z0
	logger.info("----------------------------------")
	logger.info("changes z0 to " + str(z0) + " [m]")
	# looping over us until convergence with measurements 
	notConverged = 1
	iteration = 1
	# initial guess - according to flat terrain
	us = UM*k/math.log(yM/z0)
	logger.info("us = " + str((100*us//1)*0.01))
	while notConverged:
		y_minus,Ux_y_minus,Uy_y_minus = run3dHillBase(target0, AR, z0, us, caseType)
		# checking convergence
		UxSimulation = interp(yM,y_minus,Ux_y_minus)
		err = (UM-UxSimulation)/UM
		notConverged = abs(err)>epsilon	
		logger.info("UM = " +  str((100*UM//1)*0.01) + " ,UxSimulation = " + 
			str((100*UxSimulation//1)*0.01) + " ,error is " + str(-err*100//1) + "%")
		# changing us
		us = us/(1-err)
		logger.info("us = " +  str((100*us//1)*0.01))
		logger.info("blind correction")
		Ux_y, Uy_y = Ux_y/(1-err), Uy_y/(1-err)
		notConverged = 0
	
	# saving results in matrix
	if counter==0:
		ymat_minus = Ux_ymat_minus = Uy_ymat_minus = zeros([len(y),lenAR],float)
		ymat_minus[:,counter] , Ux_ymat_minus[:,counter] , Uy_ymat_minus[:,counter] = y_minus, Ux_y_minus, Uy_y_minus
	else:
		ymat_minus[:,counter] , Ux_ymat_minus[:,counter] , Uy_ymat_minus[:,counter] = y_minus, Ux_y_minus, Uy_y_minus

	# output
	plt.figure(100)
	plt.plot(counter*10 + Ux_y_minus,y_minus,'r')
	plt.plot(counter*10 + UM,yM,'ok')
	plt.legend(['z0 = ' + str(z0Orig),'z0 = ' + str(z0_plus),'z0 = ' + str(z0_minus),'measurement'],loc='best')
	fig1.set_facecolor('w') 

	# 5

	# calculating prediction of wind speed at 4/3*yM and 2*yM
	U43y[counter] 		= interp(yM*4/3,y,Ux_y)
	U2y[counter] 		= interp(yM*2,y,Ux_y)
	U43y_plus[counter] 	= interp(yM*4/3,y_plus,Ux_y_plus)
	U2y_plus[counter] 	= interp(yM*2,y_plus,Ux_y_plus)
	U43y_minus[counter] 	= interp(yM*4/3,y_minus,Ux_y_minus)
	U2y_minus[counter] 	= interp(yM*2,y_minus,Ux_y_minus)
	
	# returning to original z0
	z0 = z0Orig

# calculating errors
resultMat = zeros([len(U43y_plus),4],float)
resultMat[:,0] = err43_plus = (U43y_plus-U43y)/U43y
resultMat[:,1] = err43_minus = (U43y_minus-U43y)/U43y
resultMat[:,2] = err2_plus = (U2y_plus-U2y)/U2y
resultMat[:,3] = err2_minus = (U2y_minus-U2y)/U2y

# writing results to csv file TODO
savetxt('resultMat.csv',resultMat,delimiter=',')

from plotZ0Influence import main as plotResults
b()
plotResults("runs/Martinez", yM, UM, 0)

'''
fig2 = figure(200)
plt.hold(True)
plt.bar(ARvec,err43_plus ,width=0.25,color='k') 
plt.bar(ARvec,err43_minus,width=0.25,color='r') 
plt.bar(ARvec+0.25,err2_plus  ,width=0.25,color='b')
plt.bar(ARvec+0.25,err2_minus ,width=0.25,color='m')
plt.grid(which='major')
plt.grid(which='minor')
plt.title('error fpr extrapolation of measurement above hill center' )
plt.xlabel('AR (0 means flat plain)')
plt.ylabel('error [%]')
plt.legend([str(ARvec)])
fig2.set_facecolor('w') 

# theoretical error for flat terrain
z0Vec = [Davenport(z0Orig,-1), z0Orig, Davenport(z0Orig,1)]
theo_plus_2 	= ((log(yM*2/z0Vec[2])*log(yM/z0Vec[1]))/(log(yM/z0Vec[2])*log(yM*2/z0Vec[1]))-1)*100					# [m]
theo_plus_43 	= ((log(yM*4./3./z0Vec[2])*log(yM/z0Vec[1]))/(log(yM/z0Vec[2])*log(yM*4./3./z0Vec[1]))-1)*100				# [m]
theo_minus_2 	= ((log(yM*2/z0Vec[0])*log(yM/z0Vec[1]))/(log(yM/z0Vec[0])*log(yM*2/z0Vec[1]))-1)*100					# [m]
theo_minus_43 	= ((log(yM*4./3./z0Vec[0])*log(yM/z0Vec[1]))/(log(yM/z0Vec[0])*log(yM*4./3./z0Vec[1]))-1)*100				# [m]

plt.bar(-2.25,theo_plus_43 ,width=0.25,color='k') #,edgecolor='g'
plt.bar(-2.,theo_minus_43,width=0.25,color='r') 
plt.bar(-1.75,theo_plus_2  ,width=0.25,color='b')
plt.bar(-1.5,theo_minus_2 ,width=0.25,color='m')

plt.show() '''
