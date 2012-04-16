#! /usr/bin/env python
# -*- coding: utf-8 -*-

# testZ0Influence_2d.py tests the effect that choosing z0 based on satelite image has on the calculated wind speed with OpenFOAM SimpleFOAM simulation
# This is done in the following steps:
# input: a. ground shape (or shapes - should be parameterized)
#	 b. measurement at 1 location (say 10 meter above hill center)
#	 c. z0 assumption
# 1. Producing a mesh
#    A blockMesh 2d volume mesh with a surface in the shape of a ideal hill (or hill series) is created
# 2. using z0 assumption, guessing ustar, running, comparing result with simulation, and changing ustar until convergence
# 3. sampling line above comparison point for the velocity at 2*M and 4/3*yM
# 4a. running with z0+deltaz0 - according to davenport scale and assuming an error of one row in the table - and repeating steps 2 and 3
# 4b. same as 4a for Davenport scale one below
# 5. LATER repeating steps 1-4 for different geometry (say - hill aspect ratio) and delta z0 and producing a "contour map") 
#
# example call to function:
# testZ0Influence_2d.py template        	target     xM yM UM z0   AR
# testZ0Influence_2d.py 2DBumpTemplate 	Martinez2D 0 20 5 0.03 1000 16 8 5 3

# where
# template 	- the case with the appropriate dictionaries, templates and boundary conditions   
# target	- the result case base name (will be target_$Hn$)	   
# xM
# yM
# UM
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
import run2dHillBase
from hilite import hilite

subprocess.call("killall gnuplot_x11",shell=True)
subprocess.call("clear",shell=True)

# TODO learn the try thingy - here it would help
n = len(sys.argv)

if n<7:
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
AR 		= float(sys.argv[7])

# TODO dummy parameters for now - C stands for "Crude" parameters
hillName = "MartinezBump2D"
r, rC        	= 1.06, 1.2
x        	= 20
Ls       	= 2500
L        	= 1000 
L1	 	= L 	#upwind refined area posibly smaller then downwind
H 	 	= 2000	# [m]
x0, x0C 	= 2, 20

h 	 = 60   # hill heigh
k 	 = 0.4	# von Karman constant
relax 	 = 1
epsilon  = 0.01

# outer loop - over AR
lenAR = n-7
U43y = U2y = U43y_plus = U2y_plus = U43y_minus = U2y_minus = ARvec = zeros(lenAR,float)
 
for counter,ARnum in enumerate(range(7,n)):

	# looping Hn inputs
	AR = float(sys.argv[ARnum])
	print "----------------------------------"
	if AR==1000:
		print hilite("flat terrain",1,1)
		ARvec[counter] = 0
	else:
  		print hilite("AR = " + str(AR),1,1)
		ARvec[counter] = AR

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # #  	      1, 2	 	# # # # # # # # # # # # # # # #
	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	# looping over us until convergence with measurements - using Crude mesh
	notConverged = 1
	# initial guess - according to flat terrain
	us = UM*k/math.log(yM/z0)
	print hilite("z0 = " + str(z0),1,1)
	print hilite("Crude runs:",1,1)
	print hilite("initial guess of us is: " + str((100*us//1)*0.01),0,1)
	while notConverged:
		y,Ux_y,Uy_y = run2dHillBase.main(template0, target0, hillName, AR, rC, x, Ls, L, L1, H, x0C, z0, us, yM, "Crude")
		# checking convergence
		UxSimulation = interp(yM,y,Ux_y)
		err = (UM-UxSimulation)/UM
		notConverged = abs(err)>epsilon	
		print hilite("UM = " +  str((100*UM//1)*0.01) + " ,UxSimulation = " + 
				str((100*UxSimulation//1)*0.01) + " ,error is " + str(err*100//1) + "%",0,1)
		# changing us
		us = us/(1-err)*relax
		print hilite("us = " +  str((100*us//1)*0.01),0,1)
	print hilite("Refined runs:",1,1)
	notConverged = 1
	while notConverged:
		y,Ux_y,Uy_y = run2dHillBase.main(template0, target0, hillName, AR, r, x, Ls, L, L1, H, x0, z0, us, yM, "mapFields")
		# checking convergence
		UxSimulation = interp(yM,y,Ux_y)
		err = (UM-UxSimulation)/UM
		notConverged = abs(err)>epsilon	
		print hilite("UM = " +  str((100*UM//1)*0.01) + " ,UxSimulation = " + 
				str((100*UxSimulation//1)*0.01) + " ,error is " + str(err*100//1) + "%",0,1)
		# changing us
		us = us/(1-err)*relax
		print hilite("us = " +  str((100*us//1)*0.01),0,1)
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
	z0 = Davenport.Davenport(z0Orig,1)
	z0_plus = z0
	print "----------------------------------"
	print hilite("changes z0 to " + str(z0) + " [m]",1,1)
	# looping over us until convergence with measurements 
	notConverged = 1
	# initial guess - according to flat terrain
	us = UM*k/math.log(yM/z0)
	print hilite("Crude runs:",1,1)
	print hilite("initial guess of us is: " + str((100*us//1)*0.01),0,1)
	while notConverged:
		y_plus,Ux_y_plus,Uy_y_plus = run2dHillBase.main(template0, 
				target0, hillName, AR, rC, x, Ls, L, L1, H, x0C, z0, us, yM, "Crude")
		# checking convergence
		UxSimulation = interp(yM,y_plus,Ux_y_plus)
		err = (UM-UxSimulation)/UM
		notConverged = abs(err)>epsilon	
		print hilite("UM = " +  str((100*UM//1)*0.01) + " ,UxSimulation = " + 
				str((100*UxSimulation//1)*0.01) + " ,error is " + str(err*100//1) + "%",0,1)
		# changing us
		us = us/(1-err)*relax
		print hilite("us = " +  str((100*us//1)*0.01),0,1)
	notConverged = 1
	print hilite("Refinced runs:",1,1)
	while notConverged:
		y_plus,Ux_y_plus,Uy_y_plus = run2dHillBase.main(template0, 
				target0, hillName, AR, r, x, Ls, L, L1, H, x0, z0, us, yM, "mapFields")
		# checking convergence
		UxSimulation = interp(yM,y_plus,Ux_y_plus)
		err = (UM-UxSimulation)/UM
		notConverged = abs(err)>epsilon	
		print hilite("UM = " +  str((100*UM//1)*0.01) + " ,UxSimulation = " + 
				str((100*UxSimulation//1)*0.01) + " ,error is " + str(err*100//1) + "%",0,1)
		# changing us
		us = us/(1-err)*relax
		print hilite("us = " +  str((100*us//1)*0.01),0,1)

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
	z0 = Davenport.Davenport(z0Orig,-1)
	z0_minus = z0
	print "----------------------------------"
	print hilite("changes z0 to " + str(z0) + " [m]",1,1)
	# looping over us until convergence with measurements 
	notConverged = 1
	iteration = 1
	# initial guess - according to flat terrain
	us = UM*k/math.log(yM/z0)
	print hilite("Crude runs:",1,1)
	print hilite("initial guess of us is: " + str((100*us//1)*0.01),0,1)
	while notConverged:
		y_minus,Ux_y_minus,Uy_y_minus = run2dHillBase.main(template0, 
				target0, hillName, AR, rC, x, Ls, L, L1, H, x0C, z0, us, yM, "Crude")
		# checking convergence
		UxSimulation = interp(yM,y_minus,Ux_y_minus)
		err = (UM-UxSimulation)/UM
		notConverged = abs(err)>epsilon	
		print hilite("UM = " +  str((100*UM//1)*0.01) + " ,UxSimulation = " + 
			str((100*UxSimulation//1)*0.01) + " ,error is " + str(err*100//1) + "%",0,1)
		# changing us
		us = us/(1-err)*relax
		print hilite("us = " +  str((100*us//1)*0.01),0,1)
	notConverged = 1;
	print hilite("Refined runs:",1,1)
	while notConverged:
		y_minus,Ux_y_minus,Uy_y_minus = run2dHillBase.main(template0, 
				target0, hillName, AR, r, x, Ls, L, L1, H, x0, z0, us, yM, "mapFields")
		# checking convergence
		UxSimulation = interp(yM,y_minus,Ux_y_minus)
		err = (UM-UxSimulation)/UM
		notConverged = abs(err)>epsilon	
		print hilite("UM = " +  str((100*UM//1)*0.01) + " ,UxSimulation = " + 
			str((100*UxSimulation//1)*0.01) + " ,error is " + str(err*100//1) + "%",0,1)
		# changing us
		us = us/(1-err)*relax
		print hilite("us = " +  str((100*us//1)*0.01),0,1)
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
du3dz0_2 = UM/(z0Orig*log(yM/z0Orig))*(log(2*yM/z0Orig)/log(yM/z0Orig)-1)
du3dz0_43 = UM/(z0Orig*log(yM/z0Orig))*(log(4/3*yM/z0Orig)/log(yM/z0Orig)-1)
theo_plus_2 = du3dz0_2*z0Orig*(Davenport.Davenport(z0Orig,1)-z0Orig)/UM
theo_plus_43 = du3dz0_43*z0Orig*(Davenport.Davenport(z0Orig,1)-z0Orig)/UM
theo_minus_2 = du3dz0_2*z0Orig*(Davenport.Davenport(z0Orig,-1)-z0Orig)/UM
theo_minus_43 = du3dz0_43*z0Orig*(Davenport.Davenport(z0Orig,-1)-z0Orig)/UM
plt.bar(ARvec-0.25,theo_plus_43 ,width=0.25,color='k',edgecolor='g') 
plt.bar(ARvec-0.25,theo_minus_43,width=0.25,color='r',edgecolor='g') 
plt.bar(ARvec-0.5,theo_plus_2  ,width=0.25,color='b',edgecolor='g')
plt.bar(ARvec-0.5,theo_minus_2 ,width=0.25,color='m',edgecolor='g')
plt.show()
