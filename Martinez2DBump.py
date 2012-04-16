#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, math, os, re, subprocess
from os import path
from numpy import *
from pylab import *
import matplotlib.pyplot as plt
import scipy.special as sp
import csv

# reading arguments
# first is blockMeshDict location, second is hill height
n = len(sys.argv)
#L = float(sys.argv[1])
#N = float(sys.argv[2])

def main(L,N):

	A = 3.1926
	a = 180 # [m]
	H = a/3 # [m]
	X0 = X = linspace(-a,a,N)	# [m]	
	Y0 = Y = - H * 1/6.04844 * ( sp.j0(A)*sp.i0(A*X/a) - sp.i0(A)*sp.j0(A*X/a) )
	if L>0:
		X = insert(X,0,-L); X = append(X,L)
		Y = insert(Y,0,0); Y = append(Y,0)
	h = 10

	# writing CSV
	g = column_stack((0*X,X,Y))
	f = open('HillShape_X.csv','wb')
	csvWriter = csv.writer(f, delimiter=',')
	csvWriter.writerow(X)
	f.close()

	f = open('HillShape_Y.csv','wb')
	csvWriter = csv.writer(f, delimiter=',')
	csvWriter.writerow(Y)
	f.close()
	return X,Y

if __name__ == '__main__':
 main(L,N)
