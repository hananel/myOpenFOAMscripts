#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys, math, os, re, subprocess
from os import path
from numpy import (linspace, sqrt, interp, insert, append)
import matplotlib.pyplot as plt
import scipy.special as sp

hill_name_choices = ["RUSHIL", "MartinezBump2D"]

def write2dShape(file_name, H, L, sample_file, h, hill_name, AR):
    if (hill_name == "RUSHIL"):
        H = 0.117 #float(sys.argv[2]) # [m]
        # ground shape equation
        n = AR #1.0/3 n = H/a
        m = n + sqrt( n**2 + 1 )
        a = H/n # [m] hill half length
        zeta = linspace(-a,a,101)
        X = 0.5 * zeta 	* ( 1 + a**2 / ( zeta**2 + m**2 * ( a**2 - zeta**2 ) ) )
        Y = 0.5 * m * sqrt( a**2 - zeta**2 )     * ( 1 - a**2 / ( zeta**2 + m**2 * ( a**2 - zeta**2 ) ) )
        X = insert(X,0,-L); X = append(X,L)
        Y = insert(Y,0,0); Y = append(Y,0)
    elif (hill_name == "MartinezBump2D"):
        A = 3.1926
        H = 200         # [m]    
        a = H*AR     # [m]
        X0 = X = linspace(-a,a,101)    # [m]    
        Y0 = Y = - H * 1/6.04844 * ( sp.j0(A)*sp.i0(A*X/a) - sp.i0(A)*sp.j0(A*X/a) )
        X = insert(X,0,-L); X = append(X,L)
        Y = insert(Y,0,0); Y = append(Y,0)
        h = 10

    # opening file
    infile  = open(file_name,"r")
    outfile = open(file_name + "_t","w")
    N = i = 0
    polyLineStart = polyLineEnd = []
    value = 0.0
    # reading first line
    line, N = infile.readline(), N+1
    while line:
        # finding the "polyLine" lines (expecting 2)
        if line.find("polyLine")>0:
            outfile.write(line)
            # saving start of polyLine
            polyLineStart.append(N+1); i+=1 
            # writing new ground shape
            for x,y in zip(X,Y):
                groundLine = "        (     %12.10f     %12.10f    %12.10f    )\n" % (x,y,value) 
                outfile.write(groundLine)
            value = 0.1    
            # finding end of polyline
            farFromTheEnd = 1
            while farFromTheEnd:
                if line.find("(")<0 and line.find(")")>0 :
                    polyLineEnd.append(N-1)
                    farFromTheEnd = 0
                    outfile.write(line)
                line, N = infile.readline(), N+1
        else:
            outfile.write(line)
            # reading new line
            line, N = infile.readline(), N+1
    # close files
    infile.close()
    outfile.close()
    # copying original to new and viceversa
    subprocess.call("cp -r " + file_name + " " + file_name + "_temp",shell=True)
    subprocess.call("cp -r " + file_name + "_t " + file_name,shell=True)

    # Write sample file
    # changing line so that it ends at +/- 1000 m
    X0 = insert(X0,0,-1000); X0 = append(X0,1000)
    Y0 = Y
    # interpolating for a refined line
    xSample = linspace(-1000,1000,2000)
    ySample = interp(xSample,X0,Y0)
    # opening file
    infile  = open(sample_file,"r")
    outfile = open(sample_file + "_t","w")
    N = i = 0
    value = 0.0
    # reading first line
    line = infile.readline()
    while line:
        # finding the "nonuniform" line
        if line.find("points") > 0 and line.find("//") < 0:
            outfile.write(line)
            # writing new sample line shape
            for x,y in zip(xSample,ySample):
                sampleLine = "		(	 %12.10f	 %12.10f	%12.10f	)\n" % (x,y+h,value) 
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
    subprocess.call("cp -r " + sample_file + " " + sample_file + "_temp",shell=True)
    subprocess.call("cp -r " + sample_file + "_t " + sample_file,shell=True)

def main():
    # reading arguments
    # first is blockMeshDict location, second is hill height
    parser = argparse.ArgumentParser()
    parser.add_argument('--file-name', required=True)
    parser.add_argument('-H', type=float, required=True)
    parser.add_argument('-L', type=float, required=True)
    parser.add_argument('--sample-file', required=True)
    parser.add_argument('--hill-name', required=True, choices=hill_name_choices)
    parser.add_argument('--AR', type=float, required=True)
    args = parser.parse_args(sys.argv[1:])
    write2dShape(**args.__dict__)

if __name__ == '__main__':
    main()
