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
 direction distribution - vector of floating point angles in degree units

Ctrl-C stops calculation
Display progress to stdout

"""

"""
Theory of operation:

Start_with_case_file -> load terrain file - STL -> <is it big enough and ends on flat surface>{Q1}

Q1 yes -> use SnappyHexMeshDict1.template -> C1
Q1 no -> use SnappyHexMeshDict2.template -> C1

C1 -> produce series of cases -> Loop1

Loop1 -> chance BC -> run RoughnessToFoam -> run case -> sample and process results{E} -> Loop1

E -> produce report{P}

P ? compare to measurements ?
"""

import sys
import os
from argparse import ArgumentParser
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

def main(case):
    if not os.path.exists(case):
        print "case directory does not exist"
        raise SystemExit
    if not os.path.isdir(case):
        print "case is not a directory"
        raise SystemExit
    wind_dict = os.path.join(case, 'windPyFoamDict')
    if not os.path.exists(wind_dict):
        print "missing %s file" % wind_dict
        raise SystemExit
    try:
        ParsedParameterFile(wind_dict)
    except Exception, e:
        print "failed to parse windPyFoam parameter file:"
        print e
        raise SystemExit

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--case', required=True)
    args = parser.parse_args(sys.argv[1:])
    main(args.case)
