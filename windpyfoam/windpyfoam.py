#!/usr/bin/python
"""

windpyfoam

"""

"""
Minimum Requirements:

Start given a case directory.
Read the following from windPyFoamDict (OpenFOAM dictionary file):
 name of stl file - string
 is stl file a rectangular flat edge outline - boolean
 check mesh convergance - boolean
 direction distribution - vector<(weight, angle)> floating point, angle in degrees. 0 <= weight <= 1

Ctrl-C stops calculation
Display progress to stdout

Next step:
GUI for same

Other parameters:
how many processors to use (should be <= multiprocessing.cpu_count())

"""

"""
Theory of operation:

Start_with_case_file -> load terrain file - STL -> <is it big enough and ends on flat surface>{Q1}

Q1 yes -> use SnappyHexMeshDict1.template -> C1
Q1 no -> use SnappyHexMeshDict2.template -> C1

C1 -> copy selected template to ____ -> produce series of cases -> Loop1

Loop1 -> chance BC -> run RoughnessToFoam -> run case -> sample and process results{E} -> Loop1

E -> produce report{P}

P ? compare to measurements ?
"""

"""
Where is everything?

from PyFoam.Basics.TemplateFile         import TemplateFile
template = TemplateFile(selected_template_file)
template.writeToFile(temp_file_name, {parameters from windFile})

run3dHillBase contains the BC (Boundary Condition) code (run3dHillBase.py:run3dHillBase).
 - read from template

"""

import atexit
import sys

import stdio

def flush():
    sys.stdout.flush()
    sys.stderr.flush()
atexit.register(flush)

from argparse import ArgumentParser

from solvers import run_windpyfoam

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--dict', required=True)
    parser.add_argument('--no-plots', default=False, action='store_true')
    args = parser.parse_args(sys.argv[1:])
    run_windpyfoam(stdio, args.dict, args.no_plots)
