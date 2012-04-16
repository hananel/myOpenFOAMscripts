#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, math, os, re, subprocess
from os import path
from numpy import *
from pylab import *
import matplotlib.pyplot as plt
import scipy.special as sp

# reading arguments
# first is blockMeshDict location, second is hill height
sampleFile = sys.argv[1]


hillName = "MartinezBump2D"
if sampleFile:
	writeSampleDict = 1 # write a sample file for acceleration h meters above hill shape

def main(sampleFile):
	
	A = 3.1926
	a = 180 # [m]
	H = a/3 # [m]
	X = linspace(-a,a,301)	# [m]	
	Y = - H * 1/6.04844 * ( sp.j0(A)*sp.i0(A*X/a) - sp.i0(A)*sp.j0(A*X/a) )
	X = insert(X,0,1000); X = append(X,1000)
	Y = insert(Y,0,0); Y = append(Y,0)
	h = 10

	# interpolating for a refined line
	xSample = linspace(-1000,1000,2000)
	ySample = interp(xSample,X,Y)
	# opening file
	infile  = open(sampleFile,"r")
	outfile = open(sampleFile + "_t","w")
	N = i = 0
	value = 0.0
	# reading first line
	line = infile.readline()
	while line:
		# finding the "nonuniform" line
		if line.find("points")>0 and line.find("//")<0:
			outfile.write(line)
			# writing new sample line shape
			for x,y in zip(xSample,ySample):
				sampleLine = "		(	 %12.10f	 %12.10f	%12.10f	)\n" % (x,value, y+h) 
				outfile.write(sampleLine)
			line = infile.readline()
		else:
			outfile.write(line)
			# reading new line
			line = infile.readline()
	# close files
	infile.close()
	outfile.close()
	# copying original to new and viceversa
	subprocess.call("cp -r " + sampleFile + " " + sampleFile + "_temp",shell=True)
	subprocess.call("cp -r " + sampleFile + "_t " + sampleFile,shell=True)
if __name__ == '__main__':
 main(sampleFile)
