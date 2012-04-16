#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, math, os
from os import path
from numpy import *
from pylab import *
import matplotlib.pyplot as plt
import os,glob,subprocess
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import rc

def main(target, yM):
	colorVec = ['r','k','b']
 	dirNameList = [x for x in glob.glob(target+'*') if not x.endswith('Crude')]
 	dirNameList.sort()

 	# defining output parameters
	lenList = len(dirNameList)
	AR = zeros(lenList,int)
	z0 = zeros(lenList,float)
 	dirNameLegend = range(lenList)
	
	for i, dirName in enumerate(dirNameList):
		print str(i) + dirName
		ARs = dirName.find('AR')
		ARe = ARs+dirName[ARs:].find('.')
		AR[i] = int(dirName[ARs+3:ARe])
		if AR[i]==1000: AR[i]=0
		z0s = dirName.find('z0')
		z0[i] = float(dirName[z0s+3:])	
	ARvec = unique(AR)
	z0Vec = unique(z0)
	Umat43 = Umat2 = zeros([len(ARvec),3],float)

	# reading data
 	for i, dirName in enumerate(dirNameList):
		ARcurrent = AR[i]
		# finding the most converged run.
  		setName = glob.glob(dirName + '/sets/*')
  		lastRun = range(len(setName))
  		for num in range(len(setName)):
   			lastRun[num] = int(setName[num][setName[num].rfind("/")+1:])
  		m = len(setName) - 1
  		p = lastRun.index(m)
  		# output to screen of convergence data
  		if not(m % 10):
   			print dirName + " did not converge, after " + str(m) + " iterations the error is TODO"
  		else:
   			print dirName + " converged after " + str(m) + " iterations"

		# y line
		# assuming all runs are with the same z0 range and different z0. so expecting three z0 numbers
		# and assuming the sorting is according to name defined by : caseStr = "_AR_" + str(AR) + "_z0_" + str(z0)
		if AR[i] == 0:
			h = 0
		else:
			h = 60 			# TODO change as input?
  		data_y = genfromtxt(setName[p] + '/line_y_U.xy',delimiter=' ')
  		y, Ux_y, Uy_y  = data_y[:,0], data_y[:,1], data_y[:,2] 
		y = y-h # normalizing data to height of hill-top above ground
		
		# plotting Uy
		fig1 = figure(i//3)
		plt.plot(Uy_y,y,color = colorVec[i%3])
		plt.grid(which='major')
		plt.grid(which='minor')
		plt.hold(True)
		plt.title('Uy above hill center' )
		plt.xlabel('Uy [m/s]')
		plt.ylabel('Vertical coordinate [m]')
		plt.legend([str(z0.min()),str(z0Vec[1]),str(z0.max())])
		fig1.set_facecolor('w') 

		# saving data - assuming sorted!
		# mat43 or mat2 contain rows of : [minus, orig, plus] for each AR
		Umat43[i//3,i%3] 	    = interp(yM*4/3,y,Ux_y)
		Umat2[i//3,i%3] 		= interp(yM*2,y,Ux_y)

	# calculating errors
	err43_plus 	= (Umat43[:,2]-Umat43[:,1])/Umat43[:,1]	*100
	err43_minus = (Umat43[:,0]-Umat43[:,1])/Umat43[:,1]	*100
	err2_plus 	= (Umat2[:,2]-Umat2[:,1])/Umat2[:,1]	*100
	err2_minus 	= (Umat2[:,0]-Umat2[:,1])/Umat2[:,1]	*100

	# plotting err
	fig2 = figure(10)
	plt.hold(True)
	plt.bar(ARvec,err43_plus ,width=0.25,color='k') 
	plt.bar(ARvec+0.25,err43_minus,width=0.25,color='r') 
	plt.bar(ARvec+0.5,err2_plus  ,width=0.25,color='b')
	plt.bar(ARvec+0.75,err2_minus ,width=0.25,color='m')
	plt.grid(which='major')
	plt.grid(which='minor')
	plt.title('error fpr extrapolation of measurement above hill center' )
	plt.xlabel('AR (0 means flat plain)')
	plt.ylabel('error [%]')
	plt.legend([str(ARvec)])
	fig2.set_facecolor('w')  
		
 	plt.show()

if __name__ == '__main__':
	# reading arguments
	n = len(sys.argv)
	if n<2:
		print "Need <TARGET> <yM>"
		sys.exit(-1)
	target    = sys.argv[1]
	yM 	  = float(sys.argv[2])
	main(target, yM)
