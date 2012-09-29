#!/usr/bin/python

import os
import sys
from os import path
from glob import glob
import multiprocessing as mp
import argparse
from PyFoam.Applications.PlotRunner import PlotRunner
from PyFoam.Applications.Runner import Runner
from PyFoam.Basics.TemplateFile     import TemplateFile
from subprocess import call
from PyFoam.RunDictionary.ParsedParameterFile   import ParsedParameterFile
import time, shutil

def run((i, args)):
    time.sleep(i*2)
    print "got %s" % repr(args)
    return PlotRunner(args=args)

def runNoPlot((i,args)):
    time.sleep(i*2)
    print "got %s" % repr(args)
    return Runner(args=args)

def runCases(args): # case_dir):
    case_dir = args.case_dir
    plotRun = args.plotRun
    cases = [x for x in glob('%s/*' % case_dir) if os.path.isdir(x)]
    start = os.getcwd()
    for case in cases:
        os.chdir(os.path.join(start, case))
        # change customeRegexp
        customRegexpName = "customRegexp.base"
        shutil.copy('/home/hanan/bin/OpenFOAM/customRegexp.base',os.path.join(start,case))
        title = "Residuals for %s" %case
        #import pdb; pdb.set_trace()
        customRegexpFile = ParsedParameterFile(customRegexpName)
        customRegexpFile["myFigure"]["theTitle"] = ('"'+title+'"')
        customRegexpFile.writeFile()
        # delete the header lines - ParsedParameterFile requires them, but the customRegexp dosen't seem to work when their around...
        lines = open(customRegexpName).readlines()
        open('customRegexp', 'w').writelines(lines[12:]) 
    os.chdir(start)

    p = mp.Pool(len(cases))
    def start_loop():
        print "args.plotRun=%d" %args.plotRun
        if args.plotRun:
            for result in \
                p.imap_unordered(run, enumerate([
                       ("--progress --frequency=10  --no-continuity --no-default simpleFoam -case %s" % case).split()
                       for case in cases])):
                print "plotRunner: got %s" % (result)
        else:
            for result in \
                p.imap_unordered(runNoPlot, enumerate([
                       ("--progress simpleFoam -case %s" % case).split()
                       for case in cases])):
                print "Runner: got %s" % (result)
    try:
        start_loop()
    except KeyboardInterrupt:
        try:
            p.close()
            p.join()
        except KeyboardInterrupt:
            p.terminate()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case-dir', help='directory of cases to use', default='.')
    parser.add_argument('--plotRun', type=bool, default=False,help='run plotRunner. If false - run pyFoamRunner.py')
    args = parser.parse_args(sys.argv[1:])
    runCases(args) #**args.__dict__)

if __name__ == '__main__':
    main()
