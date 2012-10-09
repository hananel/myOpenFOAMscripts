#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, math, os, subprocess, glob
from os import path
from numpy import *
from pylab import *
import os,glob,subprocess
from Davenport import Davenport
import pdb
b = pdb.set_trace
from argparse import ArgumentParser
import scipy.interpolate as sc
from PyFoam.Applications.PlotRunner         import PlotRunner
from PyFoam.Execution.BasicRunner       import BasicRunner
import sfoam

def main(target, caseType): 
    dirNameList = [x for x in glob.glob(target+'*') if not x.endswith('Crude')]
    cwd = os.getcwd()
    for i, dirName in enumerate(dirNameList):
        reWriteBlockMeshDict(dirName, caseType)
    
    # now that all cases have been changed - run them again
    runCases(args)
        #sfoam.sfoam(main="pyFoamRunner.py", tasks=1, progname="/home/hanan/bin/OpenFOAM/sfoam.py")

def reWriteBlockMeshDict(target, caseType):
    # read dictionaries of target case - with 3 different z0 (assuming standard case, 0.1, 0.03 and 0.005
    z0Str = target[target.find("z0")+3:]
    dict005Name = target.replace(z0Str,"0.005")
    dict03Name = target.replace(z0Str,"0.03")
    dict1Name = target.replace(z0Str,"0.1")

    # - just for memory sake ... dict005 = ParsedBlockMeshDict(target.replace(z0Str,"0.005")+"/constant/polyMesh/blockMeshDict")
    # - just for memory sake... dict03["blocks"][4][1] = dict005["blocks"][4][1]
   
    # erase all previous mesh files
    # for 0.03 case
    curDir = os.getcwd()
    os.chdir(dict03Name)
    os.chdir('constant/polyMesh')
    os.system("rm -rf *")
    os.chdir(curDir)
    
    # for 0.1 case
    os.chdir(dict1Name)
    os.chdir('constant/polyMesh')
    os.system("rm -rf *")
    os.chdir(curDir)

    # copy the 0.005 blockMeshDict to the 0.03 and 0.1 cases
    os.system("cp %s %s" % (dict005Name+"/constant/polyMesh/blockMeshDict", dict03Name+"/constant/polyMesh/blockMeshDict") )
    os.system("cp %s %s" % (dict005Name+"/constant/polyMesh/blockMeshDict", dict1Name+"/constant/polyMesh/blockMeshDict") )
    
    # running blockMesh on 0.03 case
    blockRun = BasicRunner(argv=["blockMesh",'-case',dict03Name],silent=True,server=False,logname="blockMesh")
    blockRun.start()
    if not blockRun.runOK(): print "there was an error with blockMesh"
    
    # running blockMesh on 0.005 case
    blockRun = BasicRunner(argv=["blockMesh",'-case',dict1Name],silent=True,server=False,logname="blockMesh")
    blockRun.start()
    if not blockRun.runOK(): print "there was an error with blockMesh"

   	# mapping fields - From earlier result if exists
    if caseType == "mapFields":
        # copying 0 time files from Crude run - because mapFields won't start with a non similar p and points size 
        os.system('cp -r ' + dict03Name + 'Crude/0/* ' + dict03Name + '/0/')
        os.system('cp -r ' + dict1Name + 'Crude/0/* ' + dict1Name + '/0/')
        
        # finding the most converged run. assuming the "crude" run had the same dirName with "Crude" attached
        # for z0 = 0.03
        mapRun = BasicRunner(argv=['mapFields -consistent -sourceTime latestTime' +
			 ' -case ' + dict03Name + ' ' + dict03Name + "Crude"],silent=True,server=False,logname='mapLog')
        mapRun.start()
	    # for z0 = 0.1
        mapRun = BasicRunner(argv=['mapFields -consistent -sourceTime latestTime' +
			 ' -case ' + dict1Name + ' ' + dict1Name + "Crude"],silent=True,server=False,logname='mapLog')
        mapRun.start()	

if __name__ == '__main__':
    # reading arguments
    parser = ArgumentParser()
    parser.add_argument('--target', required=True , help="target directory")
    parser.add_argument('--caseType', default="mapFields" , help="mapFields or nothing") 
    args = parser.parse_args(sys.argv[1:])
    main(args.target, args.caseType)
