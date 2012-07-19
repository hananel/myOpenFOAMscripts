#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, math, os, re, subprocess
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pylab import ginput
import csv
from numpy import *
from pylab import *
import matplotlib.pyplot as plt
import scipy.special as sp


# RIX calculation

# definition
# from Reuven WAsP course presentations
# fraction (in %) of steep terrain within specified length (say 3.5 km) from a point of interest
# steep means terrain slope above steepValue (say 0.3 or 0.4)

def RIX2D(shape,point,distance,dx,steepValue):
    # shape      = tuple of x and y of the shape (hill, hill bunch, vally etc.)
    # point      = x coordinate of point of interest
    # distance   = distance from point to be included in calculations (downwind from point)
    # dx         = discritization of shape
    # steepValue = value of dy/dx considered steep
    
    # interpolating to dx
    minX = min(shape[:][0])
    maxX = max(shape[:][0])
    xVec = linspace(minX,maxX,(maxX-minX)/dx+1)
    yVec = interp(xVec,shape[:][0],shape[:][1])
    N = len(xVec)
    slope = zeros(N)    
    slopeCounter = 0
    for i,x in enumerate(xVec):
        if(point<x and (point+distance)>x): 
            slopeCounter = slopeCounter + 1
            if i==0: 	
                # calculating slope according to first order upwind differences
                slope[i] = abs((yVec[i+1]-yVec[i]) / (xVec[i+1]-xVec[i]))
            elif i==N: 	
                # calculating slope according to first order downwind differences
                slope[i] = abs((yVec[i]-yVec[i-1]) / (xVec[i]-xVec[i-1]))    # /dx
            else: 		
                # calculating slope according to central differences
                slope[i] = abs((yVec[i+1]-yVec[i-1]) / (xVec[i+1]-xVec[i-1]))# /2*dx
    
    RIX = float(sum(slope>steepValue))/(slopeCounter)
            
    return RIX

def RIXequivalent2D(shape,point,distance,dx,steepValue):
    # shape      = tuple of x and y of the shape (hill, hill bunch, vally etc.)
    # point      = x coordinate of point of interest
    # distance   = distance from point to be included in calculations (downwind from point)
    # dx         = discritization of shape
    # steepValue = value of dy/dx considered steep
    
    # interpolating to dx
    minX = min(shape[:][0])
    maxX = max(shape[:][0])
    xVec = linspace(minX,maxX,(maxX-minX)/dx+1)
    yVec = interp(xVec,shape[:][0],shape[:][1])
    N = len(xVec)
    slope = zeros(N)    
    slopeCounter = 0
    for i,x in enumerate(xVec):
        if(point<x and (point+distance)>x): 
            slopeCounter = slopeCounter + 1
            if i==0: 	
                # calculating slope according to first order upwind differences
                slope[i] = abs((yVec[i+1]-yVec[i]) / (xVec[i+1]-xVec[i]))
            elif i==N: 	
                # calculating slope according to first order downwind differences
                slope[i] = abs((yVec[i]-yVec[i-1]) / (xVec[i]-xVec[i-1]))    # /dx
            else: 		
                # calculating slope according to central differences
                slope[i] = abs((yVec[i+1]-yVec[i-1]) / (xVec[i+1]-xVec[i-1]))# /2*dx
    
    RIX = float(sum(slope))/(slopeCounter)
            
    return RIX
