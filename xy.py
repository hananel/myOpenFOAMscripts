#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, math, os, re, subprocess
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from pylab import ginput
import csv
import pdb
b = pdb.set_trace

n = len(sys.argv)
print n

def main(argv):
	# filename = image file
	filename = os.path.realpath(argv[1])
	print filename
	c=mpimg.imread(filename)
	fig=plt.imshow(c)
	plt.draw()

	# the next values should be input for the specific chart
	# use the new opened sketch to decide what they should be
	minX=float(input('minX: '))
	maxX=float(input('maxX: '))
	minY=float(input('minY: '))
	maxY=float(input('maxY: '))

	data = np.asarray(ginput(n=-5,show_clicks=True, timeout=-5))
	X,Y = data[:,0],data[:,1]
	x = []; y = []
	for a,b in zip(X,Y):
		x.append(a)
		y.append(b)

	# first point: min x
	# second point: max x
	# third point: min y
	# fourth point: max y
	# next points - the graph itself.

	TetaX=np.arctan2((y[1]-y[0]),(x[1]-x[0]))
	CosX=np.cos(TetaX)
	SinX=np.sin(TetaX)
	SinTeta=SinX
	CosTeta=CosX

	xOut = x[0:len(x)]
	yOut = y[0:len(y)]

	for i,(xx,yy) in enumerate(zip(x,y)):
		xOut[i] = xx*CosTeta-yy*SinTeta
		yOut[i] = xx*SinTeta+yy*CosTeta

	xOut0, xOut1 = xOut[0], xOut[1]
	yOut2, yOut3 = yOut[2], yOut[3]

	xo = (xOut-xOut0)/(xOut1-xOut0)*(maxX-minX)+minX
	yo = (yOut-yOut2)/(yOut3-yOut2)*(maxY-minY)+minY

	xOut = xo[4:len(xo)]
	yOut = yo[4:len(yo)]
	g = np.column_stack((xOut,yOut))
	f = open('temp.csv','wb')
	csvWriter = csv.writer(f, delimiter=' ')
	csvWriter.writerows(g)
	f.close()

	print xOut
	print yOut

if __name__ == '__main__':
	main(sys.argv)
