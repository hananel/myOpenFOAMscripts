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
from PyFoam.Applications.ClearCase import ClearCase
from PyFoam.Applications.Decomposer import Decomposer
import time, shutil
import sfoam

def runCasesFiles(cases, runArg, n):
    start = os.getcwd()
    for case in cases:
        os.chdir(case)
        # change customeRegexp
        customRegexpName = "customRegexp.base"
        shutil.copy('/home/hanan/bin/OpenFOAM/customRegexp.base',case)
        title = "Residuals for %s" %case
        customRegexpFile = ParsedParameterFile(customRegexpName)
        customRegexpFile["myFigure"]["theTitle"] = ('"'+title+'"')
        customRegexpFile.writeFile()
        # delete the header lines - ParsedParameterFile requires them, but the customRegexp dosen't seem to work when their around...
        lines = open(customRegexpName).readlines()
        open('customRegexp', 'w').writelines(lines[12:]) 
        print n
        #  if n>1 make sure case is decomposed into n processors
        if n > 1:
            print "decomposing %(case)s" % locals()
            ClearCase(" --processors-remove %(case)s" % locals())
            Decomposer('--silent %(case)s %(n)s' % locals()) 

    #print "sfoam debug:", repr(sys.argv)
    os.chdir(start)

    p = mp.Pool(len(cases))
    def start_loop():
        print "runArg=%s" % runArg
        functions = {'plotRunner': run,
                     'Runner': runNoPlot,
                     'sfoam':runsfoam,}
        func = functions[runArg]
        pool_run_cases(p, cases, n, func)
    try:
        start_loop()
    except KeyboardInterrupt:
        try:
            p.close()
            p.join()
        except KeyboardInterrupt:
            p.terminate()

def runCases(args):
    case_dir = args.case_dir
    runArg = args.runArg
    n = args.n
    cases = [x for x in glob('%s*' % os.path.join(os.getcwd(), case_dir)) if os.path.isdir(x)]
    runCasesFiles(cases=cases, runArg=runArg, n=n)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case-dir', help='directory of cases to use', default='.')
    parser.add_argument('--runArg', default="sfoam",help='choices are: plotRunner, Runner and sfoam')
    parser.add_argument('--n',default=1,help="number of processors for each parallel run. default is 1")
    args = parser.parse_args(sys.argv[1:])
    runCases(args)

def pool_run_cases(p, cases, n, f):
    if n > 1:
        procnr_args = '--procnr %s' % n
    else:
        procnr_args = ''
    args = list(enumerate([(case,
               ("--progress %(procnr_args)s simpleFoam -case %(case)s" % locals()).split())
               for case in cases]))
    for result in p.imap_unordered(f, args):
        print "%s: got %s" % (f.func_name, result)

def run((i, (target, args))):
    time.sleep(i * 2)
    print "got %s" % repr(args)
    return PlotRunner(args=args)

def runNoPlot((i, (target, args))):
    time.sleep(i * 2)
    print "got %s" % repr(args)
    return Runner(args=args)

def runsfoam((i, (target, args))):
    time.sleep(i * 2)
    print "---------------------- %s" % args
    n = args.pop(5) # that's where n gets stored
    print "sfoam - chdir to %s" % os.getcwd()
    print "calling sfoam target=%r" % target
    return sfoam.sfoam(main="pyFoamRunner.py", tasks=n, target=target, progname="/home/hanan/bin/OpenFOAM/sfoam.py") 

if __name__ == '__main__':
    main()
