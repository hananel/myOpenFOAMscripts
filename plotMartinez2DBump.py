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

# reading arguments
n = len(sys.argv)
if n<1:
  print "Need <TARGET>"
  sys.exit(-1)

target    = sys.argv[1]
hSample = 10

def main(target, hSample):
 	dirNameList = glob.glob(target + "*")
 	dirNameList.sort()
 	print "\nPlotting the following cases:"
 	print dirNameList

 	h = 60 			# Martinez case 
 
 	dirNameLegend = range(len(dirNameList))
 	for i, dirName in enumerate(dirNameList):
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

		# x line
  		data_h = genfromtxt(setName[p] + '/line_h_U.xy',delimiter=' ')
  		x, Ux_h, Uy_h  = data_h[:,0], data_h[:,1], data_h[:,2] 

		# y line
  		data_y = genfromtxt(setName[p] + '/line_y_U.xy',delimiter=' ')
  		y, Ux_y, Uy_y  = data_y[:,0], data_y[:,1], data_y[:,2] 
		y = y-h # normalizing data to height of hill-top above ground

		# inlet
  		data_inlet = genfromtxt(setName[p] + '/line_inlet_U.xy',delimiter=' ')
  		y_inlet, Ux_inlet, Uy_inlet  = data_inlet[:,0], data_inlet[:,1], data_inlet[:,2] 

  		# calculating S_x
		Ux_inlet_hSample = interp(hSample,y_inlet,Ux_inlet)
		Sx = (Ux_h - Ux_inlet_hSample)/Ux_inlet_hSample
		
		# calculating S_y
		Sy = (Ux_y - interp(y,y_inlet,Ux_inlet))/interp(y,y_inlet,Ux_inlet)

		# calculating normolized TKE_x
		data_h_k = genfromtxt(setName[p] + '/line_h_epsilon_k_nut_p.xy',delimiter=' ')
		k = data_h_k[:,2]
		TKEn = k/(Ux_inlet_hSample**2)
		
		# plotting sample lines and acceleration numbers
		import Martinez2DBump
		X,Y = Martinez2DBump.main(3000,100)
		fig0 = figure(0)
		plt.plot(X,Y,'k',X,Y+10,'k-.',[-1500,-1500],[0,300],'r-.',[0,0],[60,360],'b-.')
		plt.legend(['hill shape','10 meter above terrain','inlet','maximum height'])
		# quiver
		arrowNum = 40
		xq_inlet, xq_top = -1500 + 0*linspace(0,1,arrowNum), 0*linspace(0,1,arrowNum)
		yq_inlet = yq_top = linspace(0,200,arrowNum)
		uq_inlet, uq_top = interp(yq_inlet,y_inlet,Ux_inlet), interp(yq_top,y,Ux_y)
		vq = xq_inlet*0
		Q = quiver(xq_inlet, yq_inlet, uq_inlet, vq, angles='xy',scale=200,color='r')
		Q = quiver(xq_top, 60+ yq_top, uq_top, vq, angles='xy',scale=100,color='b')
		qk = quiverkey(Q, -1400, 550, 10, r'$10 \frac{m}{s}$', coordinates='data',
                fontproperties={'weight': 'bold'})
		plt.axis([-1600,400,0,600])
		fig0.set_facecolor('w')
		""
		# plotting S_x
  		fig1 = figure(1)
		plt.plot(x,Sx,'.k')
		plt.grid(which='major')
  		plt.grid(which='minor')
  		plt.hold(True)
  		plt.title('Sx for h = ' + str(hSample) + ' meters' )
  		plt.ylabel('Sx')
  		fig1.set_facecolor('w')
		# adding Martinez results
		data_Martinez = genfromtxt('Martinez_Figure21a.csv',delimiter=',')
		x_Martinez, Sx_Martinez = data_Martinez[:,0], data_Martinez[:,1]
		plt.plot(x_Martinez,Sx_Martinez,'ro')
		plt.legend(['OF2.1','Martinez'])
		fig1.set_facecolor('w')
		
		# plotting TKE_x
		fig2 = figure(2)
		plt.plot(x,TKEn,'.')
		plt.grid(which='major')
  		plt.grid(which='minor')
  		plt.hold(True)
  		plt.title('TKEn for h = ' + str(hSample) + ' meters' )
  		plt.ylabel('TKEn')
  		plt.xlabel('Horizontal coordinate [m]')
		fig2.set_facecolor('w')
		# adding Martinez results
		data_M = genfromtxt('Martinez_Figure21b.csv')
		x_Martinez, TKE_Martinez = data_M[:,0], data_M[:,1]
		plt.plot(x_Martinez,TKE_Martinez,'ro')
		plt.legend(['OF2.1','Martinez'])
		fig1.set_facecolor('w')

		# plotting S_y
		fig3 = figure(3)
		plt.semilogy(Sy,y,'.')
		plt.grid(which='major')
  		plt.grid(which='minor')
  		plt.hold(True)
  		plt.title('Sy above hill center' )
  		plt.xlabel('Sy')
  		plt.ylabel('Vertical coordinate [m]')
		# adding Martinez results
		data_M = genfromtxt('Martinez_Figure21c.csv')
		y_Martinez, Ux_y_Martinez = data_M[:,0], data_M[:,1]
		plt.semilogy(y_Martinez,Ux_y_Martinez,'ro')
		plt.legend(['OF2.1','Martinez'])
		fig3.set_facecolor('w')  
		

 	plt.show()

if __name__ == '__main__':
 main(target, hSample)
