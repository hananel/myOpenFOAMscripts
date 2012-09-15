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

def processCase_2dHill(template0, target0, hillName, AR, r, x, Ls, L, L1, H, x0, z0, us, yM, h, caseType):

	caseStr = "_AR_" + str(AR) + "_z0_" + str(z0)
	if caseType=="Crude": caseStr = caseStr + "Crude"
  	target = target0+caseStr
  	
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


