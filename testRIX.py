#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, math, os, re, subprocess
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from numpy import *
from pylab import *
import matplotlib.pyplot as plt
import scipy.special as sp
import csv
import RIX
import pdb
b = pdb.set_trace

def testRIX():
    N = 500
    H = 60.
    ARVec = linspace(1,30,30)
    dx = H/50
    RIX = RIXequivalent = zeros([len(ARVec),1]) 
    for i,AR in enumerate(ARVec):
        RIXequivalent[i] = RIX.RIXequivalent2D(hill_Martinez2D(H,AR,N),0,AR*H,dx, 0.3)
        RIX[i] = RIX.RIX2D(hill_Martinez2D(H,AR,N),0,AR*H,dx, 0.3)
    plt.plot(ARVec,RIXequivalent,'rx') #,ARVec,RIX,'og')
    plt.legend(('RIX','RIXequivalent'))
    show()
	
def hill_Martinez2D(H,AR,N):
		A = 3.1926	
		a = H*AR 	# [m]
		X = linspace(-a,a,N)	# [m]	
		Y = - H * 1/6.04844 * ( sp.j0(A)*sp.i0(A*X/a) - sp.i0(A)*sp.j0(A*X/a) )
		return X,Y
		
if __name__ == '__main__':
testRIX()				
