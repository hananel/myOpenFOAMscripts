#! /usr/bin/env python
# -*- coding: utf-8 -*-

# makeBlockMesh4SHM.py creates a block mesh oriented in the desired direction for use as the SHM background mesh
# the template blockMeshDict file should already have the block and boundaries defined.
# All that is changed is the points and the spacing is calculated to maintain a 1 aspect ratio

# where
# 
#
# example run makeBlockMesh4SHM.py Askervein_template Askervein_SHM_2 598167.367 6339602.511 10000 10000 30 200 1000 120

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
		<x0> 				\n\
		<y0>  \n\
		<l - length of rectangle (in flow direction) > \n\
		<d - width of rectangele > 	\n\
		<phi - angle to north (clock wise) of flow direction> 	\n\
		<cell - length of each cell> \n\
		<a	- length of central hill> \n\
		<H	- height of central hill> \n\
		: remark: assuming z direction is ground"	
  sys.exit(-1)

template0 = sys.argv[1]			# case template (which includes all the .template files and terrain.stl) 
target0  = target = sys.argv[2]		# case target (will be created)
x0        = float(sys.argv[3]) 		# x location of center of grid
y0        = float(sys.argv[4]) 		# y location of center of grid
l       = float(sys.argv[5])		# length of rectangle (in flow direction)
d        = float(sys.argv[6])		# width of rectangele
phi       = pi/180*float(sys.argv[7])	# angle to north (clock wise) of flow direction
cell	 = int(sys.argv[8])		# length of each cell
a	= float(sys.argv[9])		# length of central hill
H	= float(sys.argv[10])		# height of central hill

# case definitions - Askervein
z0 = 0.03 	# [m]
ks = 19.58 * z0 # [m] Martinez 2011
Href = 6500	# [m] artinez 2011
us = 0.6110	# [m/s] 
k = 0.4
Uref = us/k*log(Href/z0)	# [m/s] 
zz = 1111.0	# [m]

procnr = 8

orig = SolutionDirectory(template0,
			  archive=None,
			  paraviewLink=False)
#--------------------------------------------------------------------------------------
# cloaning case
#--------------------------------------------------------------------------------------
work = orig.cloneCase(target0)

#--------------------------------------------------------------------------------------
# creating blockMeshDict
#--------------------------------------------------------------------------------------
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
# changing ABLconditions 
#--------------------------------------------------------------------------------------

# 1: changing ABLConditions
bmName = path.join(work.initialDir(),"include/ABLConditions")
template = TemplateFile(bmName+".template")
template.writeToFile(bmName,{'us':us,'Uref':Uref,'Href':Href,'z0':z0,'xDirection':sin(phi),'yDirection':cos(phi)})
# 2: changing initialConditions
#bmName = path.join(work.initialDir(),"include/initialConditions")
#template = TemplateFile(bmName+".template")
#template.writeToFile(bmName,{'TKE':TKE})

#--------------------------------------------------------------------------------------
# running SHM
#--------------------------------------------------------------------------------------
print "calculating SHM parameters"
# calculating refinement box positions
l1, l2, h1, h2 = 2*a, 1.3*a, 4*H, 2*H # refinement rulls - Martinez 2011
refBox1_minx, refBox1_miny, refBox1_minz = x0 - l1/sin(phi), y0 - l1/cos(phi), 0 #enlarging too take acount of the rotation angle
refBox1_maxx, refBox1_maxy, refBox1_maxz = x0 + l1/sin(phi), y0 + l1/cos(phi), h1 #enlarging too take acount of the rotation angle
refBox2_minx, refBox2_miny, refBox2_minz = x0 - l2/sin(phi), y0 - l2/cos(phi), 0 #enlarging too take acount of the rotation angle
refBox2_maxx, refBox2_maxy, refBox2_maxz = x0 + l2/sin(phi), y0 + l2/cos(phi),h2 #enlarging too take acount of the rotation angle
# changing snappyHexMeshDict
snapName = path.join(work.systemDir(),"snappyHexMeshDict")
template = TemplateFile(snapName+".template")
print snapName + ".template"
#template.writeToFile(bmName,{'refBox1_minx':refBox1_minx,'refBox1_miny':refBox1_miny,'refBox1_minz':refBox1_minz,'refBox1_maxx':refBox1_maxx,'refBox1_maxy':refBox1_maxy,'refBox1_maxz':refBox1_maxz,'refBox2_minx':refBox2_minx,'refBox2_miny':refBox2_miny,'refBox2_minz':refBox2_minz,'refBox2_maxx':refBox2_maxx,'refBox2_maxy':refBox2_maxy,'refBox2_maxz':refBox2_maxz,'locInMesh_x':x0,'locInMesh_y':y0,'locInMesh_z':zz})
print refBox1_minx
template.writeToFile(snapName,{'refBox1_minx':refBox1_minx})


print "wow"
SHMrun = BasicRunner(argv=["snappyHexMesh",'-overwrite','-case',work.name],server=False,logname="SHM")
print "Running SHM"
SHMrun.start()

sys.exit(6)
#--------------------------------------------------------------------------------------
# running decomposePar
#--------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------
# running SimpleFoam
#--------------------------------------------------------------------------------------
machine = LAMMachine(nr=procnr)
# run case
PlotRunner(args=["--proc=%d"%procnr,"--with-all","--progress","simpleFoam","-case",work.name])
#PlotRunner(args=["simpleFoam","-parallel","- proc =% d " % procnr, "-case",work.name])
print "work.name = ", work.name
Runner(args=["reconstructPar","-latestTime","-case",work.name])


# plotting
if plotMartinez:
	import plotMartinez2DBump
	plotMartinez2DBump.main(target,hSample)
	plt.show()
elif plotAll:
	import plot2dHill
 	plot2dHill.main(target,"U phi k TI")
 	plt.show()



