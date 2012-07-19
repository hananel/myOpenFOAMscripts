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
from Davenport import Davenport
import pdb
b = pdb.set_trace

def main(target, yM, UM, flatFlag):
	colorVec = ['r','k','b']
	
 	dirNameList = [x for x in glob.glob(target+'*') if not x.endswith('Crude')]

 	# defining output parameters
	lenList = len(dirNameList)
	AR = zeros(lenList,int)
	h = zeros(lenList,int)
	z0 = zeros(lenList,float)
 	dirNameLegend = range(lenList)

	for i, dirName in enumerate(dirNameList):
		ARs = dirName.find('_AR')
		ARe = ARs+dirName[ARs:].find('.')
		AR[i] = int(dirName[ARs+4:ARe])
		z0s = dirName.find('z0')
		z0[i] = float(dirName[z0s+3:])	
	ARvec = unique(AR)
	ARvec.sort()
	if flatFlag:
		ARvec[len(ARvec)-1]=25
	z0Vec = unique(z0)
	Umat43 , Umat2 = zeros([len(ARvec),3],float), zeros([len(ARvec),3],float)	
	Umat = zeros([len(ARvec),3,5000])
	
	import matplotlib.cm as mplcm
	import matplotlib.colors as colors
	import numpy as np

	NUM_COLORS=len(ARvec)
	cm = plt.get_cmap('gist_rainbow')
	cNorm  = colors.Normalize(vmin=0, vmax=NUM_COLORS-1)
	scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)

	# sorting
	temp = zip(AR,dirNameList)
	temp.sort()
	dirNameList = [x[1] for x in temp]

	for i, dirName in enumerate(dirNameList):
		ARs = dirName.find('_AR')
		ARe = ARs+dirName[ARs:].find('.')
		AR[i] = int(dirName[ARs+4:ARe])
		z0s = dirName.find('z0')
		z0[i] = float(dirName[z0s+3:])	
		hs = dirName.find('_h_')
		he = hs+dirName[hs:].find('_AR')
		if AR[i]==1000:
			h[i] = 0
		else:
			h[i] = int(dirName[hs+3:he])
		
	# reading data
 	for i, dirName in enumerate(dirNameList):
		ARcurrent = ARvec[i//3]
		# finding the most converged run.
  		setName = glob.glob(dirName + '/sets/*')
  		lastRun = range(len(setName))
  		for num in range(len(setName)):
   			lastRun[num] = int(setName[num][setName[num].rfind("/")+1:])
  		m = max(lastRun)
  		p = lastRun.index(m)
  		
  		# output to screen of convergence data
  		if not(m % 10):
   			print dirName + " did not converge, after " + str(m) + " iterations the error is TODO"
  		else:
   			print dirName + " converged after " + str(m) + " iterations"

		# y line
		# assuming all runs are with the same z0 range and different z0. so expecting three z0 numbers
		# and assuming the sorting is according to name defined by : caseStr = "_AR_" + str(AR) + "_z0_" + str(z0)
		
  		data_y = genfromtxt(setName[p] + '/line_y_U.xy',delimiter=' ')
  		y, Ux_y, Uy_y  = data_y[:,0], data_y[:,1], data_y[:,2]
		y = y-h[i] # normalizing data to height of hill-top above ground
		
		# applying linear factor to dictate Um at yM
		Ux_yM = interp(yM,y,Ux_y)
		
		Ux_y = Ux_y * UM/Ux_yM # normalizing speed to UM at yM
		
		# y line
		# assuming all runs are with the same z0 range and different z0. so expecting three z0 numbers
		# and assuming the sorting is according to name defined by : caseStr = "_AR_" + str(AR) + "_z0_" + str(z0)
		
  		data_inlet = genfromtxt(setName[p] + '/line_inlet_U.xy',delimiter=' ')
  		y_inlet, Ux_inlet, Uy_inlet  = data_inlet[:,0], data_inlet[:,1], data_inlet[:,2]
		Ux_inlet = Ux_inlet * UM/Ux_yM # normalizing speed to UM at yM above hill
		
		# calculating speed increase factor
		S = 0
		Ux_inlet_interp = interp(y,y_inlet,Ux_inlet)
		S = (Ux_y - Ux_inlet_interp)/Ux_inlet_interp
		
		# plotting Uy
		fig1 = figure(1)
		plt.subplot(3,1+len(ARvec)//3,1+i//3)
		plt.plot(Ux_y,y,color = colorVec[i%3])
		plt.grid(which='major')
		plt.grid(which='minor')
		plt.hold(True)
		if AR[i] == 1000:
			plt.title('flat plane')
		else:
			plt.title('AR ' + str(ARcurrent))
		if i%3==0:
			plt.ylabel('y [m]')
		if i>(len(ARvec)-2):
			plt.xlabel('Uy [m/s]')
		
		fig1.set_facecolor('w') 
		
		# plotting S_y on top of hill
		fig2 = figure(2)
		plt.subplot(3,1+len(ARvec)//3,1+i//3)
		plt.plot(S,y,color = colorVec[i%3])
		plt.grid(which='major')
		plt.grid(which='minor')
		plt.hold(True)
		if AR[i] == 1000:
			plt.title('flat plane')
		else:
			plt.title('AR ' + str(ARcurrent))
		if i%3==0:
			plt.ylabel('y [m]')
		if i>(len(ARvec)-2):
			plt.xlabel('S')
		
		# saving data - assuming sorted!
		# mat43 or mat2 contain rows of : [minus, orig, plus] for each AR

		Umat43[i//3,i%3] 		= interp(yM*4/3,y,Ux_y)
		Umat2[i//3,i%3] 		= interp(yM*2,y,Ux_y)
		if i==0:
			Umat = zeros([len(ARvec),3,len(y)])
		Umat[i//3,i%3,:]			= Ux_y
	

	# adding legend
	legend([str(z0Vec[0]),str(z0Vec[1]),str(z0Vec[2])],loc=2)
	
	#plotting error vs. z/h for different AR
	fig3 = plt.figure(3);

	for i, ARi in enumerate(ARvec):
	
		# err_plus
		ax = fig3.add_subplot(3,1,1)
		color = cm(1.*i/NUM_COLORS)  # color will now be an RGBA tuple
		err_plus = (Umat[i,2,:]-Umat[i,1,:])/Umat[i,1,:]	*100
		plt.plot(err_plus,y)
	
		# err_minus
		ax = fig3.add_subplot(3,1,2)
		color = cm(1.*i/NUM_COLORS)  # color will now be an RGBA tuple
		err_minus = (Umat[i,0,:]-Umat[i,1,:])/Umat[i,1,:]	*100
		plt.plot(y,err_minus)
		
		# sum of errors
		ax = fig3.add_subplot(3,1,3)
		color = cm(1.*i/NUM_COLORS)  # color will now be an RGBA tuple
		err = abs(err_minus)+abs(err_plus)
		plt.plot(err,y)
		
	# plotting S vs. AR for different z/h	
	
			
	# calculating errors
	err43_plus 	= (Umat43[:,2]-Umat43[:,1])/Umat43[:,1]	*100
	err43_minus = (Umat43[:,0]-Umat43[:,1])/Umat43[:,1]	*100
	err2_plus 	= (Umat2[:,2]-Umat2[:,1])/Umat2[:,1]	*100
	err2_minus 	= (Umat2[:,0]-Umat2[:,1])/Umat2[:,1]	*100

	# plotting err
	fig2 = figure(10)
	ax = subplot(2,1,1)
	plt.hold(True)
	bark = plt.bar(ARvec,err43_plus ,width=0.25,color='k') 
	barr = plt.bar(ARvec+0.5,err2_plus  ,width=0.25,color='r')
	plt.bar(ARvec+0.25,err43_minus,width=0.25,color='k') 
	plt.bar(ARvec+0.75,err2_minus ,width=0.25,color='r')
	plt.grid(which='major')
	plt.grid(which='minor')
	plt.legend((bark[0], barr[0]),(r'$\frac{4}{3}\cdot y_m$',r'$2\cdot y_m$'),loc=4)
	# TODO 2 line title below
	plt.suptitle('z0 induced error for extrapolation of velocity measurement above hill center',fontsize=16)
	plt.title('for nominal z0 = ' + str(z0Vec[1]) + ' and z0 error from ' + str(z0Vec[0]) + ' to ' + str(z0Vec[2]) + '[m]')
	plt.xlabel('AR')
	plt.ylabel('error [%]')
	fig2.set_facecolor('w')  

	# theoretical error for flat terrain
	theo_plus_2 	= ((log(yM*2/z0Vec[2])*log(yM/z0Vec[1]))/(log(yM/z0Vec[2])*log(yM*2/z0Vec[1]))-1)*100					# [m]
	theo_plus_43 	= ((log(yM*4./3./z0Vec[2])*log(yM/z0Vec[1]))/(log(yM/z0Vec[2])*log(yM*4./3./z0Vec[1]))-1)*100				# [m]
	theo_minus_2 	= ((log(yM*2/z0Vec[0])*log(yM/z0Vec[1]))/(log(yM/z0Vec[0])*log(yM*2/z0Vec[1]))-1)*100					# [m]
	theo_minus_43 	= ((log(yM*4./3./z0Vec[0])*log(yM/z0Vec[1]))/(log(yM/z0Vec[0])*log(yM*4./3./z0Vec[1]))-1)*100				# [m]
	
	plt.bar(30,theo_plus_43 ,width=0.25,color='k',edgecolor='g')
	plt.bar(30.25,theo_minus_43,width=0.25,color='k',edgecolor='g') 
	plt.bar(30.5,theo_plus_2  ,width=0.25,color='r',edgecolor='g')
	plt.bar(30.75,theo_minus_2 ,width=0.25,color='r',edgecolor='g')
	ax.text(28,3.2,'Theorethical')
	if flatFlag:
		ax.text(23	,3.22,'Flat plane')
	
	subplot(2,1,2)
	plt.hold(True)
	plt.bar(ARvec,err43_plus-err43_minus ,width=0.25,color='k') 
	plt.bar(ARvec+0.25,err2_plus-err2_minus,width=0.25,color='r') 
	plt.grid(which='major')
	plt.grid(which='minor')
	# TODO 2 line title below
	plt.xlabel('AR')
	plt.ylabel('error [%]')
	fig2.set_facecolor('w')  

	plt.bar(30,theo_plus_43-theo_minus_43 ,width=0.25,color='k',edgecolor='g')
	plt.bar(30.25,theo_plus_2-theo_minus_2  ,width=0.25,color='r',edgecolor='g')

	# plotting S
	
 	plt.show()
	
if __name__ == '__main__':
	# reading arguments
	n = len(sys.argv)
	if n<4:
		print "Need <TARGET> <yM> <UM> <flatFlag>"
		sys.exit(-1)
	target    = sys.argv[1]
	yM 	  = float(sys.argv[2])
	UM    = float(sys.argv[3])
	flatFlag 	  = float(sys.argv[4])
	main(target, yM, UM, flatFlag)
