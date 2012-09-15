#!/usr/bin/python

import os
import sys
from os import path
from glob import glob
import multiprocessing as mp
import argparse
from PyFoam.Applications.PlotRunner import PlotRunner
from PyFoam.Basics.TemplateFile     import TemplateFile
from subprocess import call
from PyFoam.RunDictionary.ParsedParameterFile   import ParsedParameterFile
import time, shutil

def run((i, args)):
    time.sleep(i*2)
    print "got %s" % repr(args)
    return PlotRunner(args=args)

def runCases(case_dir):
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
        for result in \
            p.imap_unordered(run, enumerate([
                       ("--progress --frequency=10  --no-continuity --no-default simpleFoam -case %s" % case).split()
                       for case in cases])):
            print "got %s" % (result)
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
    args = parser.parse_args(sys.argv[1:])
    runCases(**args.__dict__)

if __name__ == '__main__':
    main()
