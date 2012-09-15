#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from vtk import *
#set the fileName for the current case
myFileName = '/home/hanan/OpenFOAM/hanan-2.1.1/run/buisness/cases/trailer/cuttingPlane/1700/p_yNormal.vtk'
myFileName = '/home/hanan/OpenFOAM/hanan-2.1.1/run/buisness/cases/trailer/VTK/trailer_0.vtk'
#Need a reader for unstructured grids
reader = vtkUnstructuredGridReader()
reader.SetFileName(myFileName)
reader.Update()
#In OpenFOAM all results are Field-data.
#This has no concept of cells or nodes.
#Need to filter to cells.
toCellFilter = vtkFieldDataToAttributeDataFilter()
toCellFilter.SetInput(reader.GetOutput())
toCellFilter.SetInputFieldToCellDataField()
toCellFilter.SetOutputAttributeDataToCellData()

#Assign here which field
#we are interested in.
toCellFilter.SetScalarComponent(0,'p',0)
#This is all we need to do do calculations.
#To get 3D image, need some more components.
#First a window
renWin = vtkRenderWindow()

#Then a renderer. Renders data to an image.
ren1 = vtkRenderer()
#Add renderer to window
renWin.AddRenderer(ren1)
#Add pressure data to the renderer.
#Mapping assigns data to colors and geometry.
mapper = vtkDataSetMapper()
mapper.SetInput(toCellFilter.GetOutput())

#The object is assigned to an actor.
actor = vtkActor()
actor.SetMapper(mapper)
#Add actor to renderer.
ren1.AddActor(actor)
#Finally render image
renWin.Render()

