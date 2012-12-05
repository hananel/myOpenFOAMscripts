#! /usr/bin/env python
# -*- coding: utf-8 -*-

import math, sys
from PyFoam.RunDictionary.ParsedParameterFile 	import ParsedParameterFile
from Davenport import Davenport

inputDict = ParsedParameterFile("windPyFoamDict")
z0 		= inputDict["simParams"]["z0"]
zp_z0 = inputDict["SHMParams"]["cellSize"]["zp_z0"]
r = inputDict["SHMParams"]["cellSize"]["r"]
L = inputDict["SHMParams"]["cellSize"]["layers"]
levelRef = inputDict["SHMParams"]["cellSize"]["levelRef"]
cell	= inputDict["caseTypes"]["windRose"]["blockMeshCellSize"]
z0Vec = [Davenport(z0,-1),z0,Davenport(z0,1)]

n = len(sys.argv)
if len(sys.argv)>1:
	for fNum in range(1,n):
		fLayerRatio = float(sys.argv[fNum])
		firstLayerSize = fLayerRatio * cell / (r**(L-1)*2**levelRef)
		z0_zp = firstLayerSize/(2*z0)
		print "for fLayerRatio = " + str(fLayerRatio) + " z0 = " + str(z0) + ", z0_zp = " + str(z0_zp)
else:
	for z0 in z0Vec:
		firstLayerSize = 2*zp_z0*z0
		fLayerRatio = firstLayerSize*r**(L-1)*2**levelRef / cell
		print "for z0 = " + str(z0) + " firstLayerRatio = " + str(fLayerRatio)
