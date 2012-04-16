#!/usr/bin/python
from numpy import *
from pylab import *
import matplotlib.pyplot as plt
import os,glob,subprocess
from matplotlib.backends.backend_pdf import PdfPages

# template
import sys
if len(sys.argv)<2:
  print "Need <TEMPLATE>"
  sys.exit(-1)
template = sys.argv[1]


def main(template):
	pp = PdfPages('multipage.pdf')

	# zp vector - TODO learn how to read blockMeshDict file properly
	zDomain = 75
	scaleList=array([53, 		53, 		53,		53,		53,		53	])
	z0List =  array([0.001,		0.005, 		0.01, 	 	0.03, 		0.05, 		0.1	])
	zpList =  array([0.5017910227,  0.5017910227,	0.5017910227,	0.5017910227, 0.5248781643 ,0.5017910227])/2
	ksList = 19.58 * z0List
	a0 = (zpList/ksList).round(decimals=2)
	a1 = (zpList/z0List).round(decimals=2)

	# running through directory - finding all relevant cases
	dirNameList = glob.glob(template + '*')
        dirNameList.sort()
        print "\nPlotting the following cases:"
        print dirNameList
        dirNameLegend = range(len(dirNameList))
	for i, dirName in enumerate(dirNameList):
         legendString = "z0 = " + dirNameList[i][len(template):] + ", zp = " + str(a0[i]) + "ks, zp = " + str(a1[i]) + "z0"
         dirNameLegend[i] = legendString
	 # finding the most converged run.
	 setName =  glob.glob(dirName + '/sets/*')
	 # if sets doesnt exist - run sample
	 if setName==[]:
	  arg = " -case " + dirName + "/"
	  print arg
	  subprocess.call("sample"+ arg,shell=True)
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
	 
         # plotting k and epsilon error's over y
	 # TODO should be more general. at the moment - assuming 4000 vs. 0, and U, k, epsilon and  
	 print "calculating k & epsilon error in y direction for z0 = %s" % dirName
         start, end = 0, 4000
	 data = genfromtxt(setName[p] + '/lineX' + str(start) + '_k_nut_p_epsilon.xy',delimiter=' ')
	 y, k0, eps0 = data[:,0] , data[:,1], data[:,4]
	 data = genfromtxt(setName[p] + '/lineX' + str(end) + '_k_nut_p_epsilon.xy',delimiter=' ')
	 k1 , eps1 = data[:,1], data[:,4]
	 errk, errEpsilon = (k1-k0)/k0, (eps1-eps0)/eps1
	 c = matplotlib.cm.hot(i/10.,1)
         fig1 = figure(1)
	 plt.semilogy(100*errk,y,color=c)
	 plt.grid(which='major')
         plt.grid(which='minor')
	 plt.hold(True)

         fig3 = figure(3)
         plt.semilogy(100*errEpsilon,y,color=c)
         plt.grid(which='major')
         plt.grid(which='minor')
         hold(True)

         # plotting Ux error over y
         print "calculating Ux error in y direction for z0 = %s" % dirName
	 fig2 = figure(2)
	 # TODO should be more general. at the moment - assuming 4000 vs. 0, and U, k, epsilon and  
	 start, end = 0, 4000
	 data = genfromtxt(setName[p] + '/lineX' + str(start) + '_U.xy',delimiter=' ')
	 Ux0 = data[:,1]
	 data = genfromtxt(setName[p] + '/lineX' + str(end) + '_U.xy',delimiter=' ')
	 Ux1 = data[:,1]
	 errUx = (Ux1-Ux0)/Ux0
	 plt.semilogy(100*errUx,y,color=c)
	 plt.grid(which='major')
         plt.grid(which='minor')
	 hold(True)

         # plotting k along x error
	 # TODO should be more general. at the moment - assuming 4000 vs. 0, and U, k, epsilon and  
	 print "calculating k error in x direction for z0 = %s\n" % dirName
         case1, case2 = 50, 100
	 data = genfromtxt(setName[p] + '/lineY' + str(case1) + '_k_nut_p_epsilon.xy',delimiter=' ')
	 x, ky_case1 = data[:,0], data[:,1]
	 errky_case1 = (ky_case1 - average(k0))/average(k0)
         data = genfromtxt(setName[p] + '/lineY' + str(case2) + '_k_nut_p_epsilon.xy',delimiter=' ')
         fig4 = figure(4)
	 plt.plot(x,100*errky_case1,color=c)
	 plt.grid(which='major')
         plt.grid(which='minor')
	 hold(True)
	 x, ky_case2 = data[:,0], data[:,1]
	 errky_case2 = (ky_case2-average(k0))/average(k0)
         fig5 = figure(5)
         plt.plot(x,100*errky_case2,color=c)
         plt.grid(which='major')
         plt.grid(which='minor')
         hold(True)
        
        #legends and such
        figure(1)
        plt.title('k error')
	plt.xlabel('error %')
	plt.ylabel('vertical coordinate [m]')
	plt.legend(dirNameLegend,loc=0)
        fig1.set_facecolor('w')
        pp.savefig()

        figure(2)
	plt.title('Ux error')
	plt.xlabel('error %')
        plt.ylabel('vertical coordinate [m]')
        plt.legend(dirNameLegend,loc=0)
        fig2.set_facecolor('w')
        pp.savefig()

        figure(3)
        plt.title('$\epsilon$ error')
        plt.xlabel('error %')
        plt.ylabel('vertical coordinate [m]')
        plt.legend(dirNameLegend,loc=0)
        fig3.set_facecolor('w')
        pp.savefig()   
    
        figure(4)
        plt.title('k error - streamwise, at 50 meter')
        plt.xlabel('horizontal coordinate [m]')
        plt.ylabel('error %')
        plt.legend(dirNameLegend,loc=0)
        fig4.set_facecolor('w')
        pp.savefig()

        figure(5)
        plt.title('k error - streamwise, at 100 meter')
        plt.xlabel('horizontal coordinate [m]')
        plt.ylabel('error %')
        plt.legend(dirNameLegend,loc=0)
        fig5.set_facecolor('w')
        pp.savefig()
        pp.close()
        plt.show()

if __name__ == '__main__':
	main(template)
