#!/usr/bin/python

"""
usage:

sfoam.py -n 16 --main pyFoamPlotRunner.py --procnr=8 --machine_file=machinesPy simpleFoam
"""

from shutil import rmtree
from tempfile import mkdtemp
import os
import sys
from cStringIO import StringIO
from argparse import ArgumentParser
import atexit

tmpdirs = []

def cleanup(*arg):
    for t in tmpdirs:
        rmtree(t)

def re_matches(l):
    ret = [[]]
    s = StringIO(l)
    c = s.read(1)
    while True:
        if c == '[':
            c = s.read(1)
            if c == '':
                raise Exception('malformed regular expression')
            opts = []
            opt_start = []
            hyphen = -1
            while c != ']':
                if c == '-':
                    hyphen = len(opt_start)
                elif c == ',':
                    if hyphen != -1:
                        a, b = ''.join(opt_start[:hyphen]), ''.join(opt_start[hyphen:])
                        #print "%r, %s, %r (%r)" % (a, hyphen, b, opt_start)
                        opts.extend([list(str(x)) for x in range(int(a), int(b) + 1)])
                    else:
                        opts.append(opt_start)
                    opt_start = []
                    hyphen = -1
                else:
                    opt_start.append(c)
                c = s.read(1)
                if c == '':
                    raise Exception('malformed regular expression')
            if opt_start != []:
                if hyphen != -1:
                    a, b = ''.join(opt_start[:hyphen]), ''.join(opt_start[hyphen:])
                    #print "%r, %s, %r (%r)" % (a, hyphen, b, opt_start)
                    opts.extend([list(str(x)) for x in range(int(a), int(b) + 1)])
                else:
                    opts.append(opt_start)
            new_ret = [[r + o for o in opts] for r in ret]
            ret = sum(new_ret, [])
        else:
            for r in ret:
                r.append(c)
        c = s.read(1)
        if len(c) == 0:
            break
    return [''.join(r) for r in ret]

def test_re_matches():
    def test_one(exp, expected):
        print "testing %s" % exp
        l = re_matches(exp)
        print "result %s" % l
        assert(l == expected)
    test_one('n5', ['n5'])
    test_one('n[5,6]', ['n5', 'n6'])
    import pdb; pdb.set_trace()
    test_one('n[5-6]', ['n5', 'n6'])
    test_one('n[5,12-14]', ['n5', 'n12', 'n13', 'n14'])
    test_one('n[5,7-8,12-14]', ['n5', 'n7', 'n8', 'n12', 'n13', 'n14'])

def parse_slurm_nodelist():
    slurm_node_list = os.environ['SLURM_NODELIST']
    slurm_node_list_alt = os.environ['SLURM_JOB_NODELIST']
    if slurm_node_list != slurm_node_list_alt:
        print "mismatch between SLURM_NODELIST = %r" % slurm_node_list
        print "         and SLURM_JOB_NODELIST = %r" % slurm_node_list_alt
        assert(False)
    # n[5,7-8,12-14]
    return re_matches(slurm_node_list)

def create_machine_file():
    machine_dir = mkdtemp()
    tmpdirs.append(machine_dir)
    machine_file = os.path.join(machine_dir, 'machines')
    node_list = parse_slurm_nodelist()
    with open(machine_file, 'w+') as fd:
        fd.writelines(x + '\n' for x in node_list)
    return machine_dir, machine_file

def sfoam(main,tasks,target,progname,name): 
    atexit.register(cleanup)
    #test_re_matches()
    #raise SystemExit
    if 'SLURM_JOBID' in os.environ:
        machine_dir, machine_file = create_machine_file()
        print "machine_file = %s" % machine_file
        if not(target is "."):
            os.chdir(target)
        print "in salloc, calling %s" % main
        if tasks==1:
            os.system("%(main)s --silent simpleFoam " % locals())
        else:

            os.system("%(main)s --procnr=%(tasks)s --silent --machinefile=%(machine_file)s simpleFoam " % locals())
    else:
        print "calling salloc for OpenFOAM"
        os.system("salloc -J %(name)s -n %(tasks)s %(progname)s --n %(tasks)s --main %(main)s --target %(target)s" % locals())

def main():
    parser = ArgumentParser()
    parser.add_argument('--main', default="pyFoamRunner.py", help="name of executable for salloc")
    parser.add_argument('--target', default=".", help="case directory. runs from local directory as default")
    parser.add_argument('--n', type=int, default=1, help='number of tasks')
    parser.add_argument('--name', default='sfoam.py', help='task name')
    args = parser.parse_args(sys.argv[1:])
    main = args.main
    tasks = args.n
    target = args.target
    progname = sys.argv[0]
    name = args.name
    print "main = %s, n = %s, target = %s" % (args.main, args.n, args.target)
    sfoam(main=main, tasks=tasks, target=target, progname=progname, name=name)

if __name__ == '__main__':
    main()
