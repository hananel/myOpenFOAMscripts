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
if n<2:
  print "Need <TARGET> <arguments>"
  sys.exit(-1)

target    = sys.argv[1]
plotArguments = sys.argv[2]

def main(target, plotArguments):
 dirNameList = glob.glob(target + "*")
 dirNameList.sort()
 print "\nPlotting the following cases:"
 print dirNameList

 h = 0.117 			# RUSHIL value
 h_05a = 0.07054463130455361	# height at half hill width
 # figure line colors
 col = matplotlib.cm.gist_rainbow
 c0 = col(1/8.,1)
 c1 = col(2/8.,1)
 c2 = col(3/8.,1)
 c3 = col(4/8.,1)
 c4 = col(5/8.,1)
 c5 = col(6/8.,1)
 c6 = col(7/8.,1)  
 
 # finding out how many arguments to plot
 subPlotLength = n-2
 subPlotCounter = 1
 plotU = plotphi = plotk = plotR = plotTI = 0
 if any('U' in sys.argv): 
  plotU=1
 if any('phi' in sys.argv): 
  plotphi=1
 if any('k' in sys.argv): 
  plotk=1
 if any('TI' in sys.argv): 
  plotTI=1
 
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
 
  print "plotting U data vs simulation"
  pp = PdfPages('U_' + dirNameList[0] + '.pdf')

  data = genfromtxt(setName[p] + '/line_inlet_U.xy',delimiter=' ')
  y_inlet, Ux_inlet, Uy_inlet  = data[:,0], data[:,1], data[:,2] 
  if plotU:
   # ----------------------- U ----------------------
   # inlet
   fig0 = figure(10)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_inlet_U.xy',delimiter=' ')
   y_inlet, Ux_inlet, Uy_inlet  = data[:,0], data[:,1], data[:,2] 
   plt.plot(Ux_inlet,y_inlet,color=c0)
   data_x_inlet = genfromtxt(dirName + '/A_3H/epanhils.dat')
   yD_inlet, UD_inlet = data_x_inlet[:,1], data_x_inlet[:,2]
   plt.plot(UD_inlet,yD_inlet,'o',color = c0)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('U at x = -4 (inlet)')
   plt.xlabel('U [m/s]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig0.set_facecolor('w')
   pp.savefig()  

   # -2a
   fig1 = figure(1)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_2a_U.xy',delimiter=' ')
   y_2a, Ux_2a, Uy_2a  = data[:,0], data[:,1], data[:,2] 
   plt.plot(Ux_2a,y_2a,color=c0)
   #TODO this is done assuming U is the Ux velocity - the text is "the mean velocity first component U (in m/s), " - 
   # what is "first component" ? only X direction? has to be because it has negetive values (so can't be mean) .
   # should look in TROMBETTI, F., MARTANO, P. & TAMPIERI, F. (1991). Data sets for studies of flow and dispersion in complex  
   # terrain: I) the RUSHIL wind tunnel experiment (flow data). CNR Technical Report No.1, FISBAT-RT-91/1
   # data
   data_x_2a = genfromtxt(dirName + '/A_3H/epah31s.dat')
   yD_2, UD_2 = data_x_2a[:,1], data_x_2a[:,2]
   plt.plot(UD_2,yD_2,'o',color = c0)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('U at x = -2a')
   plt.xlabel('U [m/s]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig1.set_facecolor('w')
   pp.savefig()    
   print "error in U(y=0.8) = " + str(100*(Ux_2a[len(Ux_2a)-1] - UD_2[len(UD_2)-1]) / Ux_2a[len(Ux_2a)-1]) + "%" 

   # -1a
   fig2 = figure(2)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_1a_U.xy',delimiter=' ')
   y_1a, Ux_1a ,Uy_1a =  data[:,0], data[:,1], data[:,2]
   plt.plot(Ux_1a,y_1a,color=c1)
   # data
   data_x_1a = genfromtxt(dirName + '/A_3H/epah33s.dat')
   yD_1, UD_1 = data_x_1a[:,1], data_x_1a[:,2]
   plt.plot(UD_1,yD_1,'o',color = c1)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('U at x = -1a')
   plt.xlabel('U [m/s]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig2.set_facecolor('w')
   pp.savefig()   

   # -0.5a
   fig3 = figure(3)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_0.5a_U.xy',delimiter=' ')
   y_05a, Ux_05a ,Uy_05a =  data[:,0], data[:,1], data[:,2]
   plt.plot(Ux_05a,y_05a-h_05a,color=c2)
   # data
   data_x_05a = genfromtxt(dirName + '/A_3H/epah35s.dat')
   yD_05, UD_05 = data_x_05a[:,1], data_x_05a[:,2]
   plt.plot(UD_05,yD_05,'o',color = c2)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('U at x = -0.5a')
   plt.xlabel('U [m/s]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig3.set_facecolor('w')
   pp.savefig()    

   # 0
   fig4 = figure(4)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_0_U.xy',delimiter=' ')
   y0, Ux0 ,Uy0 =  data[:,0], data[:,1], data[:,2]
   plt.plot(Ux0,y0-h,color=c3)
   # data 
   data_x0 = genfromtxt(dirName + '/A_3H/epah37s.dat')
   yD0, UD0 = data_x0[:,1], data_x0[:,2]
   plt.plot(UD0,yD0,'o',color = c3)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('U at x = 0')
   plt.xlabel('U [m/s]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig4.set_facecolor('w')
   pp.savefig()   

   # 0.5a
   fig5 = figure(5)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line0.5a_U.xy',delimiter=' ')
   y05a, Ux05a ,Uy05a =  data[:,0], data[:,1], data[:,2]
   plt.plot(Ux05a,y05a-h_05a,color=c4)
   # data
   data_x05a = genfromtxt(dirName + '/A_3H/epah39s.dat')
   yD05, UD05 = data_x05a[:,1], data_x05a[:,2]
   plt.plot(UD05,yD05,'o',color = c4)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('U at x = 0.5a')
   plt.xlabel('U [m/s]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig5.set_facecolor('w')
   pp.savefig()    

   # 1a
   fig6 = figure(6)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line1a_U.xy',delimiter=' ')
   y1a, Ux1a ,Uy1a =  data[:,0], data[:,1], data[:,2]
   plt.plot(Ux1a,y1a,color=c5)
   # data
   data_x1a = genfromtxt(dirName + '/A_3H/epah311s.dat')
   yD1, UD1 = data_x1a[:,1], data_x1a[:,2]
   plt.plot(UD1,yD1,'o',color = c5)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('U at x = 1a')
   plt.xlabel('U [m/s]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig6.set_facecolor('w')
   pp.savefig()     

   # 2a
   fig7 = figure(7)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line2a_U.xy',delimiter=' ')
   y2a, Ux2a ,Uy2a =  data[:,0], data[:,1], data[:,2]
   plt.plot(Ux2a,y2a,color=c6)
   # data
   data_x2a = genfromtxt(dirName + '/A_3H/epah313s.dat')
   yD2, UD2 = data_x2a[:,1], data_x2a[:,2]
   plt.plot(UD2,yD2,'o',color = c6)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('U at x = 2a')
   plt.xlabel('U [m/s]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig7.set_facecolor('w')
   pp.savefig()   
   pp.close() 
   subPlotCounter += 1

  if plotR:
   # ----------------------- Reynolds stresses ----------------------
   Rdata = 4; # 1 and 4  (and perhaps 6) most likely, but shifted. 4 is sepposed to be Rxy according to an online reference i did not write down...
   pp = PdfPages('R_' + dirNameList[0] + '.pdf')
   print "plotting Reynolds stress data vs simulation"
   # Rxx, Ryy, Rzz, Rxy, Rxz, Ryz
   # -2a
   fig1 = figure(1)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_2a_R.xy',delimiter=' ')
   Rxy_2a = data[:,Rdata] # <1> = too big, same shape, shifted by a lot, <2> = negetive, <3>=0, <4>=too big not exact shape,  <5> = 0, <6> = too big not exact shape
   plt.plot(Rxy_2a,y_2a,color=c0)
   uv_2 = data_x_2a[:,6]
   plt.plot(uv_2,yD_2,'o',color = c0)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('Rxy (-uv) at x = -2a')
   plt.xlabel('R [m^2/s^2]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig1.set_facecolor('w')
   pp.savefig()    
   print "error in R(y=0.8) = " + str(100*(Rxy_2a[len(Rxy_2a)-1] - uv_2[len(uv_2)-1]) / Rxy_2a[len(Rxy_2a)-1]) + "%"

   # -1a
   fig2 = figure(2)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_1a_R.xy',delimiter=' ')
   Rxy_1a =  data[:,Rdata]
   plt.plot(Rxy_1a,y_1a,color=c1)
   # data
   uv_1 = data_x_1a[:,6]
   plt.plot(uv_1,yD_1,'o',color = c1)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('R at x = -1a')
   plt.xlabel('R [m^2/s^2]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig2.set_facecolor('w')
   pp.savefig()   
   
   # -0.5a
   fig3 = figure(3)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_0.5a_R.xy',delimiter=' ')
   Rxy_05a =  data[:,Rdata]
   plt.plot(Rxy_05a,y_05a-h_05a,color=c2) #check height again
   # data
   uv_05 = data_x_05a[:,6]
   plt.plot(uv_05,yD_05,'o',color = c2)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('R at x = -0.5a')
   plt.xlabel('R [m^2/s^2]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig3.set_facecolor('w')
   pp.savefig()    

   # 0
   fig4 = figure(4)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_0_R.xy',delimiter=' ')
   Rxy0 =  data[:,Rdata]
   plt.plot(Rxy0,y0-h,color=c3)
   # data 
   uv0 = data_x0[:,6]
   plt.plot(uv0,yD0,'o',color = c3)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('R at x = 0')
   plt.xlabel('R [m^2/s^2]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig4.set_facecolor('w')
   pp.savefig()   
  
   # 0.5a
   fig5 = figure(5)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line0.5a_R.xy',delimiter=' ')
   Rxy05a =  data[:,Rdata]
   plt.plot(Rxy05a,y05a-h_05a,color=c4)
   # data
   uv05 = data_x05a[:,6]
   plt.plot(uv05,yD05,'o',color = c4)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('R at x = 0.5a')
   plt.xlabel('R [m^2/s^2]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig5.set_facecolor('w')
   pp.savefig()   

   # 1a
   fig6 = figure(6)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line1a_R.xy',delimiter=' ')
   Rxy1a =  data[:,Rdata]
   plt.plot(Rxy1a,y1a,color=c5)
   # data
   uv1 = data_x1a[:,6]
   plt.plot(uv1,yD1,'o',color = c5)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('R at x = 1a')
   plt.xlabel('R [m^2/s^2]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig6.set_facecolor('w')
   pp.savefig()     

   # 2a
   fig7 = figure(7)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line2a_R.xy',delimiter=' ')
   Rxy2a =  data[:,Rdata]
   plt.plot(Rxy2a,y2a,color=c6)
   # data
   uv2 = data_x2a[:,6]
   plt.plot(uv2,yD2,'o',color = c6)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('R at x = 2a')
   plt.xlabel('R [m^2/s^2]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig7.set_facecolor('w')
   pp.savefig()
   pp.close()  
   subPlotCounter+=1

  if plotphi: 
   # ----------------------- flow angle ----------------------
   pp = PdfPages('FlowAngle_' + dirNameList[0] + '.pdf')
   print "plotting flow angle data vs simulation"
   # inlet
   fig0 = figure(10)
   subplot(1,subPlotLength,subPlotCounter)
   phi_inlet = arctan(Uy_inlet/Ux_inlet)*180/pi
   plt.plot(phi_inlet,y_inlet,color=c0)
   phiD_inlet = data_x_inlet[:,3]
   plt.plot(phiD_inlet,yD_inlet,'o',color = c0)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('phi at x = -4 (inlet)')
   plt.xlabel('phi [degrees]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig0.set_facecolor('w')
   pp.savefig() 
   
   # -2a
   fig1 = figure(1)
   subplot(1,subPlotLength,subPlotCounter)
   phi_2a = arctan(Uy_2a/Ux_2a)*180/pi
   plt.plot(phi_2a,y_2a,color=c0)
   # data
   phi_2 = data_x_2a[:,3]
   plt.plot(phi_2,yD_2,'o',color = c0)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('flow angle at x = -2a')
   plt.xlabel('angle [deg]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig1.set_facecolor('w')
   pp.savefig()   
   print "error in flow angle (y=0.8) = " + str(100*(phi_2a[len(phi_2a)-1] - phi_2[len(phi_2)-1]) / phi_2a[len(phi_2a)-1]) + "%" 

   # -1a
   fig2 = figure(2)
   subplot(1,subPlotLength,subPlotCounter)
   phi_1a = arctan(Uy_1a/Ux_1a)*180/pi
   plt.plot(phi_1a,y_1a,color=c1)
   # data
   phi_1 = data_x_1a[:,3]
   plt.plot(phi_1,yD_1,'o',color = c1)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('flow angle at x = -1a')
   plt.xlabel('angle [deg]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig2.set_facecolor('w')
   pp.savefig()   
   
   # -0.5a
   fig3 = figure(3)
   subplot(1,subPlotLength,subPlotCounter)
   phi_05a = arctan(Uy_05a/Ux_05a)*180/pi
   plt.plot(phi_05a,y_05a-h_05a,color=c2)
   # data
   phi_05 = data_x_05a[:,3]
   plt.plot(phi_05,yD_05,'o',color = c2)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('flow angle at x = -0.5a')
   plt.xlabel('angle [deg]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig3.set_facecolor('w')
   pp.savefig()    

   # 0
   fig4 = figure(4)
   subplot(1,subPlotLength,subPlotCounter)
   phi0 = arctan(Uy0/Ux0)*180/pi
   plt.plot(phi0,y0-h,color=c3)
   # data
   phi_0 = data_x0[:,3]
   plt.plot(phi_0,yD0,'o',color = c3)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('flow angle at x = 0')
   plt.xlabel('angle [deg]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig4.set_facecolor('w')
   pp.savefig()   
   
   # 0.5a
   fig5 = figure(5)
   subplot(1,subPlotLength,subPlotCounter)
   phi05a = arctan(Uy05a/Ux05a)*180/pi
   plt.plot(phi05a,y05a-h_05a,color=c4)
   # data
   phi05 = data_x05a[:,3]
   plt.plot(phi05,yD05,'o',color = c4)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('flow angle at x = 0.5a')
   plt.xlabel('angle [deg]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig5.set_facecolor('w')
   pp.savefig()   

   # 1a
   fig6 = figure(6)
   subplot(1,subPlotLength,subPlotCounter)
   phi1a = arctan(Uy1a/Ux1a)*180/pi
   plt.plot(phi1a,y1a,color=c5)
   # data
   phi1 = data_x1a[:,3]
   plt.plot(phi1,yD1,'o',color = c5)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('flow angle at x = 1a')
   plt.xlabel('angle [deg]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig6.set_facecolor('w')
   pp.savefig()     

   # 2a
   fig7 = figure(7)
   subplot(1,subPlotLength,subPlotCounter)
   phi2a = arctan(Uy2a/Ux2a)*180/pi
   plt.plot(phi2a,y2a,color=c6)
   # data
   phi2 = data_x2a[:,3]
   plt.plot(phi2,yD2,'o',color = c6)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('flow angle at x = 2a')
   plt.xlabel('angle [deg]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig7.set_facecolor('w')
   pp.savefig()
   pp.close()
   subPlotCounter += 1

  if plotk: 
   # ----------------------- k - Turbulent Kinetic Energy ----------------------
   pp = PdfPages('k_' + dirNameList[0] + '.pdf')
   print "plotting k, data vs simulation"
   # inlet
   fig0 = figure(10)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_inlet_epsilon_k_nut_p.xy',delimiter=' ')
   k_inlet = data[:,2]
   plt.plot(k_inlet,y_inlet,color=c0)
   kD_inlet = 3.0/4.0*(data_x_inlet[:,4]**2+data_x_inlet[:,5]**2)
   plt.plot(kD_inlet,yD_inlet,'o',color = c0)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('k at x = -4 (inlet)')
   plt.xlabel('k r"\$left[\frac{m^2}{s^2}\right]$"')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig0.set_facecolor('w')
   pp.savefig() 

   # -2a
   fig1 = figure(1)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_2a_epsilon_k_nut_p.xy',delimiter=' ')
   k_2a = data[:,2]
   plt.plot(k_2a,y_2a,color=c0)
   # data
   k_2 = 3.0/4.0*(data_x_2a[:,4]**2+data_x_2a[:,5]**2)
   plt.plot(k_2,yD_2,'o',color = c0)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('k at x = -2a')
   plt.xlabel('k r"\$left[\frac{m^2}{s^2}\right]$"')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig1.set_facecolor('w')
   pp.savefig()   
   print "error in k (y=0.8) = " + str(100*(k_2a[len(k_2a)-1] - k_2[len(k_2)-1]) / k_2a[len(k_2a)-1]) + "%" 

   # -1a
   fig2 = figure(2)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_1a_epsilon_k_nut_p.xy',delimiter=' ')
   k_1a = data[:,2]
   plt.plot(k_1a,y_1a,color=c1)
   # data
   k_1 = 3.0/4.0*(data_x_1a[:,4]**2+data_x_1a[:,5]**2)
   plt.plot(k_1,yD_1,'o',color = c1)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('k at x = -1a')
   plt.xlabel('k r"\$left[\frac{m^2}{s^2}\right]$"')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig2.set_facecolor('w')
   pp.savefig()   
   
   # -0.5a
   fig3 = figure(3)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_0.5a_epsilon_k_nut_p.xy',delimiter=' ')
   k_05a = data[:,2]
   plt.plot(k_05a,y_05a-h_05a,color=c2)
   # data
   k_05 = 3.0/4.0*(data_x_05a[:,4]**2+data_x_05a[:,5]**2)
   plt.plot(k_05,yD_05,'o',color = c2)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('k at x = -0.5a')
   plt.xlabel('k r"\$left[\frac{m^2}{s^2}\right]$"')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig3.set_facecolor('w')
   pp.savefig()    

   # 0
   fig4 = figure(4)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line_0_epsilon_k_nut_p.xy',delimiter=' ')
   k0 = data[:,2]
   plt.plot(k0,y0-h,color=c3)
   # data
   k_0 = 3.0/4.0*(data_x0[:,4]**2+data_x0[:,5]**2)
   plt.plot(k_0,yD0,'o',color = c3)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('k at x = 0')
   plt.xlabel('k r"\$left[\frac{m^2}{s^2}\right]$"')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig4.set_facecolor('w')
   pp.savefig()   
   
   # 0.5a
   fig5 = figure(5)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line0.5a_epsilon_k_nut_p.xy',delimiter=' ')
   k05a = data[:,2]
   plt.plot(k05a,y05a-h_05a,color=c4)
   # data
   k05 = 3.0/4.0*(data_x05a[:,4]**2+data_x05a[:,5]**2)
   plt.plot(k05,yD05,'o',color = c4)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('k at x = 0.5a')
   plt.xlabel('k r"\$left[\frac{m^2}{s^2}\right]$"')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig5.set_facecolor('w')
   pp.savefig()   

   # 1a
   fig6 = figure(6)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line1a_epsilon_k_nut_p.xy',delimiter=' ')
   k1a = data[:,2]
   plt.plot(k1a,y1a,color=c5)
   # data
   k1 = 3.0/4.0*(data_x1a[:,4]**2+data_x1a[:,5]**2)
   plt.plot(k1,yD1,'o',color = c5)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('k at x = 1a')
   plt.xlabel('k r"\$left[\frac{m^2}{s^2}\right]$"')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig6.set_facecolor('w')
   pp.savefig()     

   # 2a
   fig7 = figure(7)
   subplot(1,subPlotLength,subPlotCounter)
   data = genfromtxt(setName[p] + '/line2a_epsilon_k_nut_p.xy',delimiter=' ')
   k2a = data[:,2]
   plt.plot(k2a,y2a,color=c6)
   # data
   k2 = 3.0/4.0*(data_x2a[:,4]**2+data_x2a[:,5]**2)
   plt.plot(k2,yD2,'o',color = c6)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('k at x = 2a')
   plt.xlabel('k r"\$left[\frac{m^2}{s^2}\right]$"')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig7.set_facecolor('w')
   pp.savefig()
   pp.close()
   subPlotCounter += 1

  if plotTI: 
   # ----------------------- Turbulence Intensity ----------------------
   pp = PdfPages('TI_' + dirNameList[0] + '.pdf')
   print "plotting TI data vs simulation"
   # inlet
   fig0 = figure(10)
   subplot(1,subPlotLength,subPlotCounter)
   TI_inlet = sqrt(k_inlet)/Ux_inlet
   plt.plot(TI_inlet,y_inlet,color=c0)
   # data
   TID_inlet = sqrt(kD_inlet)/UD_inlet
   plt.plot(TID_inlet,yD_inlet,'o',color = c0)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('TI at x = -4 (inlet)')
   plt.xlabel('TI')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig0.set_facecolor('w')
   pp.savefig()

   # -2a
   fig1 = figure(1)
   subplot(1,subPlotLength,subPlotCounter)
   TI_2a = sqrt(k_2a)/Ux_2a
   plt.plot(TI_2a,y_2a,color=c0)
   # data
   TI_2 = sqrt(k_2)/UD_2
   plt.plot(TI_2,yD_2,'o',color = c0)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('TI at x = -2a')
   plt.xlabel('TI')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig1.set_facecolor('w')
   pp.savefig()   
   print "error in TI (y=0.8) = " + str(100*(TI_2a[len(TI_2a)-1] - TI_2[len(TI_2)-1]) / TI_2a[len(TI_2a)-1]) + "%" 

   # -1a
   fig2 = figure(2)
   subplot(1,subPlotLength,subPlotCounter)
   TI_1a = sqrt(k_1a)/Ux_1a
   plt.plot(TI_1a,y_1a,color=c1)
   # data
   TI_1 = sqrt(k_1)/UD_1
   plt.plot(TI_1,yD_1,'o',color = c1)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('TI at x = -1a')
   plt.xlabel('TI')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig2.set_facecolor('w')
   pp.savefig()   
   
   # -0.5a
   fig3 = figure(3)
   subplot(1,subPlotLength,subPlotCounter)
   TI_05a = sqrt(k_05a)/Ux_05a
   plt.plot(TI_05a,y_05a-h_05a,color=c2)
   # data
   TI_05 = sqrt(k_05)/UD_05
   plt.plot(TI_05,yD_05,'o',color = c2)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('TI at x = -0.5a')
   plt.xlabel('TI')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig3.set_facecolor('w')
   pp.savefig()    

   # 0
   fig4 = figure(4)
   subplot(1,subPlotLength,subPlotCounter)
   TI0 = sqrt(k0)/Ux0
   plt.plot(TI0,y0-h,color=c3)
   # data
   TI_0 = sqrt(k_0)/UD0
   plt.plot(TI_0,yD0,'o',color = c3)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('TI at x = 0')
   plt.xlabel('TI [deg]')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig4.set_facecolor('w')
   pp.savefig()   
   
   # 0.5a
   fig5 = figure(5)
   subplot(1,subPlotLength,subPlotCounter)
   TI05a = sqrt(k05a)/Ux05a
   plt.plot(TI05a,y05a-h_05a,color=c4)
   # data
   TI05 = sqrt(k05)/UD05
   plt.plot(TI05,yD05,'o',color = c4)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('TI at x = 0.5a')
   plt.xlabel('TI')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig5.set_facecolor('w')
   pp.savefig()   

   # 1a
   fig6 = figure(6)
   subplot(1,subPlotLength,subPlotCounter)
   TI1a = sqrt(k1a)/Ux1a
   plt.plot(TI1a,y1a,color=c5)
   # data
   TI1 = sqrt(k1)/UD1
   plt.plot(TI1,yD1,'o',color = c5)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('TI x = 1a')
   plt.xlabel('TI')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig6.set_facecolor('w')
   pp.savefig()     

   # 2a
   fig7 = figure(7)
   subplot(1,subPlotLength,subPlotCounter)
   TI2a = sqrt(k2a)/Ux2a
   plt.plot(TI2a,y2a,color=c6)
   # data
   TI2 = sqrt(k2)/UD2
   plt.plot(TI2,yD2,'o',color = c6)
   plt.grid(which='major')
   plt.grid(which='minor')
   plt.hold(True)
   plt.title('TI at x = 2a')
   plt.xlabel('TI')
   plt.ylabel('vertical coordinate [m]')
   plt.legend(['simulation','RUSHIL'],loc=0)
   fig7.set_facecolor('w')
   pp.savefig()
   pp.close()   
   subPlotCounter += 1

 plt.show()

if __name__ == '__main__':
 main(target, plotArguments)
