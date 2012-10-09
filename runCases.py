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
import sfoam

def runCases(args):
    case_dir = args.case_dir
    runArg = args.runArg
    cases = [x for x in glob('%s*' % os.path.join(os.getcwd(),case_dir)) if os.path.isdir(x)]
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
    os.chdir(start)

    p = mp.Pool(len(cases))
    def start_loop():
        print "args.runArg=%s" %args.runArg
        functions = {'plotRunner': run,
                     'Runner': runNoPlot,
                     'sfoam':runsfoam,}
        func = functions[args.runArg]
        pool_run_cases(p, cases, func)
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
    parser.add_argument('--runArg', default="sfoam",help='choices are: plotRunner, Runner and sfoam')
    args = parser.parse_args(sys.argv[1:])
    runCases(args)

def run_plotRunner(p, cases):
    for result in \
        p.imap_unordered(run, enumerate([
               ("--progress --frequency=10  --no-continuity --no-default simpleFoam -case %s" % case).split()
               for case in cases])):
        print "plotRunner: got %s" % (result)

def pool_run_cases(p, cases, f):
    args = list(enumerate([(case,
               ("--progress simpleFoam --target %s" % case).split())
               for case in cases]))
    #print "pool_run_cases %s %s" % (repr(f), repr(args))
    for result in p.imap_unordered(f, args):
        print "%s: got %s" % (f.func_name, result)

def run_sfoam_hanan_no_work(p, cases):
    cwd = os.getcwd()
    for i, case in enumerate(cases):
        os.chdir(case)
        print "changed dir to %s " % (os.getcwd())
        p.imap_unordered(runsfoam, ([i, ("--main pyFoamRunner.py --n=1 progname='/home/hanan/bin/OpenFOAM/sfoam.py'")]))
        os.chdir(cwd)

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
    print "sfoam - chdir to %s" % os.getcwd()
    print "calling sfoam target=%r" % target
    return sfoam.sfoam(main="pyFoamRunner.py", tasks=1, target=target, progname="/home/hanan/bin/OpenFOAM/sfoam.py") 

if __name__ == '__main__':
    main()
