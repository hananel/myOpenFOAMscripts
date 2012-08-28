#! /usr/bin/env python
# -*- coding: utf-8 -*-
from numpy import *
import pdb
b = pdb.set_trace
def interpf(facMat,ARVec,z0Vec,AR,z0):
	mat = array(facMat)
	if z0==0.005:
		f = interp(AR,ARVec,mat[:,0])
	if z0==0.03:
		f = interp(AR,ARVec,mat[:,1])
	if z0==0.1:
		f = interp(AR,ARVec,mat[:,2])
	
	return f
