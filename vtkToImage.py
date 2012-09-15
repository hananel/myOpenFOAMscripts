#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from paraview.simple import *
import sys, glob

parser = argparse.ArgumentParser()
parser.add_argument('--vtk-file-dir', help='directory of vtk file to use', default='.')
args = parser.parse_args(sys.argv[1:])
files = glob('%s/*' % args.vtk_file_dir)

for fileName in files:
	U_yNormal_vtk = LegacyVTKReader( FileNames=[fileName] )

	RenderView1 = GetRenderView()
	DataRepresentation1 = Show()
	DataRepresentation1.ScaleFactor = 4.0
	DataRepresentation1.SelectionPointFieldDataArrayName = 'U'
	DataRepresentation1.EdgeColor = [0.0, 0.0, 0.5]

	a3_U_PVLookupTable = GetLookupTableForArray( "U", 3, NanColor=[0.25, 0.0, 0.0], RGBPoints=[0, 0.23, 0.3, 0.754, 20.1, 0.7, 0.016, 0.15], VectorMode='Magnitude', ColorSpace='Diverging', ScalarRangeInitialized=1.0 )

	a3_U_PiecewiseFunction = CreatePiecewiseFunction( Points=[0.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0] )

	RenderView1.CameraPosition = [0.0, 10.0, 90]
	RenderView1.CameraFocalPoint = [0.0, 10.0, 0]
	RenderView1.CameraClippingRange = [15, 15]
	RenderView1.CenterOfRotation = [0.0, 10.0, 0]
	RenderView1.CameraParallelScale = 20
	RenderView1.ViewSize.SetData([1600,1000])

	DataRepresentation1.ColorArrayName = 'U'
	DataRepresentation1.LookupTable = a3_U_PVLookupTable

	WriteImage(fileName + '.png')

	import subprocess
	subprocess.call(['xdg-open','a1.png'])
