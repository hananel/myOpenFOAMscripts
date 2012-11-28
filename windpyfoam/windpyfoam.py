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

import sys
import os
import multiprocessing
import itertools
import glob
import shutil
import subprocess
from datetime import datetime
from os import path
from math import pi, sin, cos, floor, log, sqrt
from argparse import ArgumentParser

from PyFoam.RunDictionary.SolutionDirectory     import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile   import ParsedParameterFile
from PyFoam.Applications.ClearCase              import ClearCase
from PyFoam.Applications.Runner                 import Runner
from PyFoam.Basics.TemplateFile                 import TemplateFile
from PyFoam.Applications.Decomposer             import Decomposer
from PyFoam.Execution.BasicRunner 		        import BasicRunner

sys.path.append('../')
from runCases import runCasesFiles as runCases

def warn(x):
    print "WARNING:", x

def debug(x):
    print "DEBUG:", x

def status(x):
    print "STATUS:", x

def create_block_mesh_dict(work, wind_dict, params):
    phi = params['phi']
    cell_size = params["cell_size"]
    SHM = wind_dict["SHMParams"]
    Href = SHM["domainSize"]["domZ"]
    domainSize = SHM["domainSize"]
    lup, ldown, d = domainSize["fXup"], domainSize["fXdown"], domainSize["fY"]
    x0, y0 = (SHM["centerOfDomain"]["x0"],
              SHM["centerOfDomain"]["y0"])
    sin_phi = sin(phi)
    cos_phi = cos(phi)
    x1 = x0 - (lup * sin_phi + d / 2 * cos_phi)
    y1 = y0 - (lup * cos_phi - d / 2 * sin_phi)
    x2 = x0 - (lup * sin_phi - d / 2 * cos_phi)
    y2 = y0 - (lup * cos_phi + d / 2 * sin_phi)
    x3 = x0 + (ldown * sin_phi + d / 2 * cos_phi)
    y3 = y0 + (ldown * cos_phi - d / 2 * sin_phi)
    x4 = x0 + (ldown * sin_phi - d / 2 * cos_phi)
    y4 = y0 + (ldown * cos_phi + d / 2 * sin_phi)
    n = floor(d / cell_size)
    m = floor((lup+ldown) / cell_size)
    q = floor((Href - domainSize["z_min"]) / cell_size)
    if n == 0 or m == 0 or q == 0:
        print "invalid input to block mesh dict:"
        print "d = %(d)f, l = %(l)f, Href = %(Href)f, cell = %(cell)f, cell_size = %(cell_size)f" % locals()
        print "n = %(n)f, m = %(m)f, q = %(q)f" % locals()
    assert(n > 0 and m > 0 and q > 0)
    bmName = path.join(work.constantDir(),"polyMesh/blockMeshDict")
    template = TemplateFile(bmName+".template")
    template.writeToFile(bmName,
        {'X0':x1,'X1':x2,'X2':x3,'X3':x4,
         'Y0':y1,'Y1':y2,'Y2':y3,'Y3':y4,
         'Z0':Href,'n':int(n),'m':int(m),'q':int(q), 'z_min':domainSize["z_min"]})

def create_SHM_dict(work, wind_dict, params):
    print "calculating SHM parameters"
    phi = params['phi']
    SHM = wind_dict["SHMParams"]
    domainSize = SHM['domainSize']
    a = domainSize['refinement_length']
    H = domainSize['typical_height']
    Href = SHM["domainSize"]["domZ"]
    cell_size = params['cell_size'] # blockMesh cell size
    z_cell = cell_size
    zz = SHM["pointInDomain"]["zz"]
    x0, y0 = (SHM["centerOfDomain"]["x0"],
              SHM["centerOfDomain"]["x0"])
    z0 = wind_dict['simParams']['z0'] # TODO: calculated per wind direction using roughness2foam
    # calculating refinement box positions
    l1, l2, h1, h2 = 2*a, 1.3*a, 4*H, 2*H # refinement rules - Martinez 2011
    sp = sin(phi)
    cp = cos(phi)
    #enlarging to take acount of the rotation angle
    def calc_box(l, h):
        tx1, ty1, tz1 = x0 - l*(sp+cp), y0 - l*(cp-sp), domainSize["z_min"]
        tx2, ty2, tz2 = x0 + l*(sp+cp), y0 + l*(cp-sp), h
        return (min(tx1, tx2), min(ty1, ty2), min(tz1, tz2),
                max(tx1, tx2), max(ty1, ty2), max(tz1, tz2))
    (refBox1_minx, refBox1_miny, refBox1_minz,
     refBox1_maxx, refBox1_maxy, refBox1_maxz) = calc_box(l1, h1)
    (refBox2_minx, refBox2_miny, refBox2_minz,
     refBox2_maxx, refBox2_maxy, refBox2_maxz) = calc_box(l2, h2)
    assert(refBox1_minx < refBox1_maxx)
    assert(refBox1_miny < refBox1_maxy)
    assert(refBox1_minz < refBox1_maxz)
    assert(refBox2_minx < refBox2_maxx)
    assert(refBox2_miny < refBox2_maxy)
    assert(refBox2_minz < refBox2_maxz)

    # changing snappyHexMeshDict - with parsedParameterFile

    # case 1 - an stl file describing a rectangular domain larger then the blockMesh control volume
    if SHM["rectanguleDomainSTL"]:
        shutil.copyfile(path.join(work.systemDir(), "snappyHexMeshDict_rectanguleDomain"), \
                    path.join(work.systemDir(), "snappyHexMeshDict"))
    # case 2 - an stl file describing a single hill, with edges at z_min
    else:
         shutil.copyfile(path.join(work.systemDir(), "snappyHexMeshDict_singleHill"), \
                    path.join(work.systemDir(), "snappyHexMeshDict"))

    # changes that apply to both cases
    SHMDict = ParsedParameterFile(
        path.join(work.systemDir(), "snappyHexMeshDict"))
    # changing refinement boxes around center reigon
    SHMDict["geometry"]["refinementBox1"]["min"] = \
        "("+str(refBox1_minx)+" "+str(refBox1_miny)+" "+str(refBox1_minz)+")"
    SHMDict["geometry"]["refinementBox1"]["max"] = \
        "("+str(refBox1_maxx)+" "+str(refBox1_maxy)+" "+str(refBox1_maxz)+")"
    SHMDict["geometry"]["refinementBox2"]["min"] = \
        "("+str(refBox2_minx)+" "+str(refBox2_miny)+" "+str(refBox2_minz)+")"
    SHMDict["geometry"]["refinementBox2"]["max"] = \
        "("+str(refBox2_maxx)+" "+str(refBox2_maxy)+" "+str(refBox2_maxz)+")"
    # changing inlet refinement reigon - crude correction to SHM layer fault at domain edges
    lup, ldown, d = domainSize["fXup"], domainSize["fXdown"], domainSize["fY"]
    x1 = x0 - (lup * sp + d / 2 * cp)
    y1 = y0 - (lup * cp - d / 2 * sp)
    x3 = x0 - ((lup - cell_size) * sp + d / 2 * cp)
    y3 = y0 - ((lup - cell_size) * cp - d / 2 * sp)

    SHMDict["geometry"]["upwindbox1"]["min"] = \
        "("+str(min(x1,x3))+" "+str(min(y1,y3))+" "+str(domainSize["z_min"])+")"
    SHMDict["geometry"]["upwindbox1"]["max"] = \
        "("+str(max(x1,x3))+" "+str(max(y1,y3))+" "+str(domainSize["z_min"]+cell_size)+")"
    """x1 = x0 + (ldown * sp + d / 2 * cp)
    y1 = y0 + (ldown * cp - d / 2 * sp)
    x3 = x0 + ((ldown - cell_size) * sp - d / 2 * cp)
    y3 = y0 + ((ldown - cell_size) * cp + d / 2 * sp)

    SHMDict["geometry"]["refinementOutlet"]["min"] = \
        "("+str(min(x1,x3))+" "+str(min(y1,y3))+" "+str(domainSize["z_min"])+")"
    SHMDict["geometry"]["refinementOutlet"]["max"] = \
        "("+str(max(x1,x3))+" "+str(max(y1,y3))+" "+str(domainSize["z_min"]+cell_size)+")"
    """
    # changing location in mesh
    SHMDict["castellatedMeshControls"]["locationInMesh"] = "("+str(x0)+" "+str(y0)+" "+str(zz)+")"
    levelRef = SHM["cellSize"]["levelRef"]
    SHMDict["castellatedMeshControls"]["refinementSurfaces"]["terrain"]["level"] = \
        "("+str(levelRef)+" "+str(levelRef)+")"
    SHMDict["castellatedMeshControls"]["refinementRegions"]["upwindbox1"]["level"] =  \
        "("+str(levelRef * 2)+" "+str(levelRef * 2)+")"
    r = SHM["cellSize"]["r"]
    SHMDict["addLayersControls"]["expansionRatio"] = r
    fLayerRatio = SHM["cellSize"]["fLayerRatio"]
    SHMDict["addLayersControls"]["finalLayerThickness"] = fLayerRatio
    # calculating finalLayerRatio for getting
    zp_z0 = SHM["cellSize"]["zp_z0"]
    firstLayerSize = 2 * zp_z0 * z0
    L = log(fLayerRatio/firstLayerSize*z_cell/2**levelRef) / log(r) + 1
    SHMDict["addLayersControls"]["layers"]["terrain_solid"]["nSurfaceLayers"] = int(round(L))

    # changes that apply only to case 2
    if not(SHM["rectanguleDomainSTL"]):
        SHMDict["geometry"]["groundSurface"]["pointAndNormalDict"]["basePoint"] = \
            "( 0 0 "+str(domainSize["z_min"])+")"
        SHMDict["castellatedMeshControls"]["refinementRegions"]["groundSurface"]["levels"] = \
            "(("+str(h2)+" "+str(levelRef)+") ("+str(h1)+" "+str(int(round(levelRef/2)))+"))"
        SHMDict["addLayersControls"]["layers"]["ground"]["nSurfaceLayers"] = int(round(L))
    SHMDict.writeFile()



def create_boundary_conditions_dict(work, wind_dict, params):
    #--------------------------------------------------------------------------------------
    # changing inlet profile - - - - according to Martinez 2010
    #--------------------------------------------------------------------------------------
    phi = params['phi']
    SHM = wind_dict['SHMParams']
    kEpsParams = wind_dict['kEpsParams']
    UM = wind_dict['simParams']['UM']
    yM = wind_dict['simParams']['yM']
    k = kEpsParams['k'] # von karman constant
    z0 = wind_dict['simParams']['z0'] # TODO: calculated per wind direction using roughness2foam
    us = UM * k / log(yM / z0)
    Href = SHM['domainSize']['domZ']
    Cmu = kEpsParams['Cmu'] # K-epsilon turbulence closure parameter
    # change inlet profile
    Uref = Utop = us / k * log(Href / z0)
    # calculating turbulentKE
    TKE = us * us / sqrt(Cmu)
    # 1: changing ABLConditions
    bmName = path.join(work.initialDir(),"include", "ABLConditions")
    template = TemplateFile(bmName + ".template")
    template.writeToFile(bmName,
        {'us':us,'Uref':Uref,'Href':Href,'z0':z0,
         'xDirection':sin(phi),'yDirection':cos(phi)})
    # 2: changing initialConditions
    bmName = path.join(work.initialDir(),"include", "initialConditions")
    template = TemplateFile(bmName + ".template")
    template.writeToFile(bmName,{'TKE':TKE})
    # 3: changing initial and boundary conditions for new z0
    # changing ks in nut, inside nutRoughWallFunction
    nutFile = ParsedParameterFile(path.join(work.initialDir(), "nut"))
    nutFile["boundaryField"]["ground"]["z0"].setUniform(z0)
    nutFile["boundaryField"]["terrain_.*"]["z0"].setUniform(z0)
    nutFile.writeFile()

def read_dict_string(d, key):
    """
    to allow using a filename like so:
    template "/home/hanan/bin/OpenFOAM/windpyfoam/test_template";

    if you remove the '"' you get an Illegal '/' used message
    """
    val = d[key]
    if len(val) > 0 and val[0] == '"':
        assert(val[-1] == '"')
        val = val[1:-1]
    return val

def create_case(wind_dict, params):
    """
     0. cloning case
     1. creating snappyHexMeshDict and blockMeshdict according to flow direction and other parameters
     2. creating the blockMesh
     3. change the boundary conditions
     4. decomposing the domain
     5. creating the snappyHexMesh - running in parallel (sfoam.py or not - depending on user input)
     6. decomposing the created mesh
    """
    #--------------------------------------------------------------------------------------
    # cloning case
    #--------------------------------------------------------------------------------------
    target = params['case_dir']
    target = os.path.realpath(target)
    if not os.path.exists(target):
        makedirs(target)
    template = read_dict_string(wind_dict, 'template')
    debug("template = %r, target = %r" % (template, target))
    orig = SolutionDirectory(template,
                             archive=None,
                             paraviewLink=False)
    work = orig.cloneCase(target)

    #--
    # creating dictionaries
    #--
    if wind_dict['procnr'] > multiprocessing.cpu_count():
        warn('wind_dict contains a higher processor number then the machine has')
        wind_dict['procnr'] = min(wind_dict['procnr'], multiprocessing.cpu_count())
    phi = params['wind_dir'] * pi / 180
    params['phi'] = phi # - pi/180 * 90

    status('creating block mesh dictionary')
    create_block_mesh_dict(work, wind_dict, params)
    status('creating snappy hex mesh dictionary')
    create_SHM_dict(work, wind_dict, params)
    status('creating boundary conditions dictionary')
    create_boundary_conditions_dict(work, wind_dict, params)
    status('running block mesh')
    run_block_mesh(work)
    status('running decompose')
    run_decompose(work, wind_dict)
    status('running snappy hex mesh')
    run_SHM(work, wind_dict)
    status('running second decompose')
    run_decompose(work, wind_dict)
    return work

def run_decompose(work, wind_dict):
    if wind_dict['procnr'] < 2:
        status('skipped decompose')
        return
    ClearCase(args=work.name+'  --processors-remove')
    Decomposer(args=[work.name, wind_dict['procnr']])

def run_block_mesh(work):
    blockRun = BasicRunner(argv=["blockMesh", '-case', work.name],
                           silent=True, server=False, logname="blockMesh")
    print "Running blockMesh"
    blockRun.start()
    if not blockRun.runOK(): error("there was an error with blockMesh")

def mpirun(procnr, argv, output_file):
    # TODO: use Popen and supply stdout for continous output monitor (web)
    assert(type(procnr), int)
    return subprocess.check_output(['mpirun', '-np', str(procnr)] + argv + ['-parallel', '-output-file', str(output_file)])

def run_SHM(work, wind_dict):
    if wind_dict["procnr"] > 1:
        print "Running SHM parallel"
        decomposeDict = ParsedParameterFile(
        path.join(work.systemDir(), "decomposeParDict"))
        decomposeDict["method"] = "ptscotch"
        decomposeDict.writeFile()
        mpirun(procnr=wind_dict['procnr'], argv=['snappyHexMesh',
            '-overwrite', '-case', work.name],output_file='log.SHM')
    else:
        SHMrun = BasicRunner(argv=["snappyHexMesh",
                               '-overwrite','-case',work.name],
                         server=False,logname="SHM")
        print "Running SHM uniprocessor"
        SHMrun.start()

def makedirs(d):
    debug('creating %r' % d)
    os.makedirs(d)

def grid_convergance_params_generator(wind_dict):
    """
    yields names of case directories
    """
    grid_convergence = wind_dict["caseTypes"]["gridConvergenceParams"]
    gridRange = grid_convergence['gridRange']
    template = read_dict_string(wind_dict, 'template')
    wind_dir = grid_convergence['windDir']
    for i, cell_size in enumerate(gridRange):
        case_dir = os.path.join(wind_dict['runs'],
                            '%(template)s_grid_%(cell_size)s' % locals())
        yield dict(case_dir=case_dir, wind_dir=wind_dir, cell_size=cell_size,
                   name='grid_convergence %d: cell_size=%d, wind_dir=%d' % (i, cell_size, wind_dir))

def wind_rose_params_generator(wind_dict):
    """
    yields names of case directories
    one for each direction from wind rose
    """
    windRose = wind_dict['caseTypes']["windRose"]
    template = read_dict_string(wind_dict, 'template')
    cell_size = windRose['blockMeshCellSize']
    for i, (_weight, wind_dir) in enumerate(windRose['windDir']):
        case_dir = os.path.join(wind_dict['runs'],
                            '%(template)s_rose_%(wind_dir)s' % locals())
        yield dict(case_dir = case_dir, wind_dir = wind_dir, cell_size = cell_size,
                   name='wind_rose %d: cell_size=%d, wind_dir=%d' % (i, cell_size, wind_dir))

def run_directory(prefix):
    now = datetime.now()
    pristine = now.strftime(prefix + '_%Y%m%d_%H%M%S')
    if os.path.exists(pristine):
        if os.path.exists(pristine + '_1'):
            last = max([try_int(x.rsplit('_', 1)[0])
                        for x in glob(pristine + '_*')])
            d = pristine + '_%d' % (last + 1)
        else:
            d = pristine + '_1'
    else:
        d = pristine
    return d

def reconstructCases(cases):
    for case in cases:
        Runner(args=["reconstructPar" ,"-latestTime", "-case" ,case])

def main(conf):
    """
    Mesh: creating the write snappyHexMeshDict file
    use the right snappyHexMeshDict_XXX.template file with wind_dict
     but --> already at this stage i have to work in a loop according to the
     amount of cases i am asked to solve. each case will be cloned from the
     template case, and then the procedure of
     if doing grid convergance with a single
     foreach dir in {winddirs, grid}:
         1. creating snappyHexMeshDict and blockMeshdict according to flow direction and other parameters
         2. creating the blockMesh
         3. decomposing the domain
         4. creating the snappyHexMesh - running in parallel (sfoam.py or not - depending on user input)
         5. decomposing the created mesh
         6. running pyFoamRunner.py through sfoam (or not - depending on user input)

     After all cases stop running
     7. if exist (usually) - reading real measurements
     8. creating sampleDict according to measurement locations and user input
        (which asks for wind speed contour map at certain height above ground)
     9. sampling (command is "sample")
     10. using the results to calculate the following metrics
        1. for a specific grid size and multiple directions and weights for
           each direction - the power density and average wind speed averaged over
           the direction at specific heights above ground level
        2. for a specific direction and different grid cell sizes - the grid
           error according to some known grid convergence algorithm
        3. a "hit rate" which shows the aggreement of the simulated wind speeds
           and turbulence to the measurements
    """
    if not os.path.exists(conf):
        print "missing %s file" % conf
        raise SystemExit
    try:
        wind_dict = ParsedParameterFile(conf)
    except Exception, e:
        print "failed to parse windPyFoam parameter file:"
        print e
        raise SystemExit
    wind_dict['runs'] = run_directory('runs')
    # running the grid convergence routine - for 1 specific direction
    gen = []
    if wind_dict["caseTypes"]["gridConvergence"]:
        gen = grid_convergance_params_generator(wind_dict)
    gen = itertools.chain(gen,
            wind_rose_params_generator(wind_dict))
    cases = []
    for params in gen:
        debug(params['name'])
        work = create_case(wind_dict, params)
        cases.append(work)
    # TODO: customizable runArg
    status('RUNNING CASES')
    runCases(n=wind_dict['procnr'], runArg='Runner',
             cases=[case.name for case in cases])
    status('DONE running cases')
    # reconstructing case
    status('Reconstructing cases')
    reconstructCases([case.name for case in cases])
    status('Sampling cases')
    # TODO  1. build sampleDict according to wind_dict measurement info
    #       2. run sample utility
    status('Ploting hit-rate')
    # TODO
    status('Ploting contour maps at specified heights')
    # TODO
    status('plotting wind rose and histogram at specified location')
    # TODO
# 5/

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--conf', required=True)
    args = parser.parse_args(sys.argv[1:])
    main(args.conf)
