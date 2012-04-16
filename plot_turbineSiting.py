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

	# finding the most converged run.
	setName =  glob.glob(template + '/sets/*')
        print setName 
	# if sets doesnt exist - run sample
	if setName==[]:
	 arg = " -case " + template + "/"
	 print arg
	 subprocess.call("sample"+ arg,shell=True)
	 setName =  glob.glob(dirName + '/sets/*')
	lastRun = range(len(setName))
	for num in range(len(setName)):
	 lastRun[num] = int(setName[num][setName[num].rfind("/")+1:])
	m = max(lastRun)
	p = lastRun.index(m)
        
        cases = [100,400,600]
	Ulegend = range(len(cases))
	for i,num in enumerate(cases):
	 print "plotting U for x = %s" % str(num)
	 data = genfromtxt(setName[p] + '/lineX' + str(num) + '_U.xy',delimiter=' ')
	 z, Ux0 = data[:,0], data[:,1]
	 z -= z[0]
	 c = matplotlib.cm.hot(i/10.,1)
         # plotting U vs z for "cases" in directory
         fig1 = figure(1)
	 plt.plot(Ux0,z,color=c)
	 plt.grid(which='major')
         plt.grid(which='minor')
	 plt.hold(True)
         # plotting U vs z for "cases" in directory
         Ex0 = 0.5*1.225*Ux0**3
         fig2 = figure(2)
	 plt.plot(Ex0,z,color=c)
	 plt.grid(which='major')
         plt.grid(which='minor')
	 plt.hold(True)
	 Ulegend[i] = 'x = ' + str(num)


        print str(cases)
        #legends and such
        figure(1)
        plt.title('Horizontal wind spead (Ux) at different x points')
	plt.xlabel('U [m/s]')
	plt.ylabel('z [m]')
	plt.axis([0,14,0,200])
	plt.legend(Ulegend,loc=0)
        fig1.set_facecolor('w')
        pp.savefig()

	figure(2)
        plt.title('Wind energy at different x points')
	plt.xlabel('E [W/m^2]')
	plt.ylabel('z [m]')
	plt.axis([0,1200,0,200])
	plt.legend(Ulegend,loc=0)
        fig2.set_facecolor('w')
	pp.savefig()

        pp.close()
        plt.show()

if __name__ == '__main__':
	main(template)
