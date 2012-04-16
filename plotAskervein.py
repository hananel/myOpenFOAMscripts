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

# figure line colors
col = matplotlib.cm.gist_rainbow
cases = sys.argv[2:]
show = float(sys.argv[1])

def main(cases):
 	dirNameList = cases
 	dirNameList.sort()
	N = len(dirNameList)+1
	dirNameLegend = range(len(dirNameList)+1)
	print dirNameLegend
 	print "\nPlotting the following cases:"
 	print dirNameList
	
	# Askervein ground height at different points (this is a problematic point - 
	# could have been deformed in the transformation from STRM to UTM, and from GB grid to UTM, and finally into STL
	hSample = 10
 	h_RS = 3.132133
	h_HT = 114.886347
	h_CP = 111.317233  
 	x_HT, y_HT = 598167.367, 6339602.511
	
	# plot color
	colLength = float(len(dirNameList)+1)

 	for i, dirName in enumerate(dirNameList):
		
		plotColor = col(i/colLength,1)

		# finding the most converged run.
  		setName =  glob.glob(dirName + '/sets/*')
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

		# line A
  		data_A = genfromtxt(setName[p] + '/line_A_U.xy',delimiter=' ')
  		x, y, z, Ux_A, Uy_A, Uz_A  = data_A[:,0], data_A[:,1], data_A[:,2], data_A[:,3], data_A[:,4], data_A[:,5]
		L = sign(x-x_HT) * sqrt((x-x_HT)**2+(y-y_HT)**2)
		U_A = sqrt(Ux_A**2 + Uy_A**2)

		# HT line
  		data_HT = genfromtxt(setName[p] + '/line_HT_U.xy',delimiter=' ')
  		z_HT, Ux_HT, Uy_HT, Uz_HT  = data_HT[:,0], data_HT[:,1], data_HT[:,2] , data_HT[:,3]
		z_HT = z_HT-h_HT # normalizing data to height of hill-top above ground
		U_HT = sqrt(Ux_HT**2 + Uy_HT**2)

		# RS line (inlet)
  		data_RS = genfromtxt(setName[p] + '/line_RS_U.xy',delimiter=' ')
  		z_RS, Ux_RS, Uy_RS, Uz_RS  = data_RS[:,0], data_RS[:,1], data_RS[:,2] , data_RS[:,3]
		z_RS = z_RS-h_RS # normalizing data to height of hill-top above ground
		U_RS = sqrt(Ux_RS**2 + Uy_RS**2)

  		# calculating S_A
		Ux_RS_hSample, Uy_RS_hSample = interp(hSample,z_RS,Ux_RS), interp(hSample,z_RS,Uy_RS)
		U_RS_hSample = sqrt(Ux_RS_hSample**2 + Uy_RS_hSample**2)
		print "U_RS_hSample = " , U_RS_hSample, " m/s"
		S_A = (U_A - U_RS_hSample)/U_RS_hSample
		
		# calculating S_HT
		S_HT = (U_HT - interp(z_HT,z_RS,U_RS))/interp(z_HT,z_RS,U_RS)

		# calculating normolized TKE_x
		data_A_k = genfromtxt(setName[p] + '/line_A_epsilon_k_nut_p.xy',delimiter=' ')
		k = data_A_k[:,4]
		TKEn = k/(U_RS_hSample**2)
		
		# plotting RS and HT horizontal wind speed profile
		fig0 = figure(0)
		plt.plot(U_RS,z_RS,U_HT,z_HT,color=plotColor)

		# plotting S_A
  		fig1 = figure(1)
		plt.plot(L,S_A,color=plotColor)
		plt.grid(which='major')
  		plt.grid(which='minor')
  		plt.hold(True)
  		plt.title('speed up along line A at ' + str(hSample) + ' meters above ground' )
  		plt.ylabel('speedup')
		plt.xlabel('length from HT along line A')		
		
		# plotting TKE_x
		fig2 = figure(2)
		plt.plot(L,TKEn,color=plotColor)
		plt.grid(which='major')
  		plt.grid(which='minor')
  		plt.hold(True)
  		plt.title('TKEn for h = ' + str(hSample) + ' meters' )
  		plt.ylabel('TKEn')
  		plt.xlabel('Horizontal coordinate [m]')

		# plotting S_HT
		fig3 = figure(3)
		plt.plot(S_HT,z_HT,color=plotColor)
		plt.grid(which='major')
  		plt.grid(which='minor')
  		plt.hold(True)
  		plt.title('speedup above hill top (HT)' )
  		plt.xlabel('speedup')
  		plt.ylabel('Vertical coordinate [m]')

		# adding dirName as legend entry
		if len(dirName)<2:
			dirName = 'OpenFoam'
		dirNameLegend[i] = dirName
		
	# adding observations and legend
	fig0 = figure(0)
	data_Martinez = genfromtxt('/sim/Askervein/obs/TU03-B_RS_HT.dat')
	z_Martinez, U_RS_Martinez, U_HT_Martinez = data_Martinez[:,0], data_Martinez[:,1], data_Martinez[:,2]
	plt.plot(U_RS_Martinez,z_Martinez,'ko',U_HT_Martinez,z_Martinez,'ko')
	plt.legend(['RS OpenFOAM','RS observations','HT OpenFOAM','HT observations'],loc=0)
	plt.title('Profile comparisons, HT and RS')
  	plt.xlabel('U [m/s]')
  	plt.ylabel('Vertical coordinate [m]')
	fig0.set_facecolor('w')
	plt.savefig('fig0.png')

	dirNameLegend[i+1] = 'observations'
	fig1 = figure(1)
	data_S_A = genfromtxt('/sim/Askervein/obs/obs_A_10mSpeedup.dat')
	L_obs, S_A_obs, S_A_obs_min, S_A_obs_max = data_S_A[:,0], data_S_A[:,1], data_S_A[:,2], data_S_A[:,3]
	plt.errorbar(L_obs,S_A_obs,[S_A_obs-S_A_obs_min,S_A_obs_max-S_A_obs],fmt='ko')
	plt.legend(dirNameLegend,loc=0)
	plt.axis([-1000, 600, -1, 1])
	fig1.set_facecolor('w')
	plt.savefig('fig1.png')

	fig2 = figure(2)
	data_TKE_obs = genfromtxt('/sim/Askervein/obs/obs_A_10mTurbulence.dat')
	L_obs, TKE_A_obs = data_TKE_obs[:,0], data_TKE_obs[:,1]
	plt.plot(L_obs,TKE_A_obs,'ko')
	plt.legend(dirNameLegend,loc=0)
	plt.axis([-1000, 600, 0.01, 0.07])
	fig2.set_facecolor('w')
	plt.savefig('fig2.png')

	fig3 = figure(3)
	plt.plot((U_HT_Martinez-U_RS_Martinez)/U_RS_Martinez,z_Martinez,'ko')
	plt.legend(dirNameLegend,loc=0)
	fig3.set_facecolor('w')
	plt.savefig('fig3.png')
 	if show:
		plt.show()

if __name__ == '__main__':
 main(cases)
