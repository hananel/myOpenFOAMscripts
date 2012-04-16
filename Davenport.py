#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

def Davenport(z0, d):
	dav = np.array([0.0002, 0.005, 0.03, 0.1, 0.25, 0.5, 1, 2])
	if d > 0:
		sign = 1
	elif d < 0:
		sign = -1
	elif d == 0:
		sign=0
	else :
		print "insert a number for direction"
	return float(dav[dav.searchsorted(z0)+sign])

