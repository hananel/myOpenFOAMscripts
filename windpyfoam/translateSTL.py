#!/usr/bin/python
     
import sys
import os
     
"""
 facet normal 0.0000 0.0302 -0.0302
 outer loop
 vertex -67.0000 3.8597 1.0000
 vertex -67.1060 3.8940 1.0000
 vertex -67.0000 4.1445 1.0000
"""
     
def main():
    try:
        dz = float(sys.argv[-1])
    except:
        print "usage: %s <delta z> < input.stl > output.stl" % sys.argv[0]
        raise SystemExit
    if len(sys.argv) == 4:
        stl_shift_z_filenames(sys.argv[1], sys.argv[2], dz)
    else:
        stl_shift_z_streams(sys.stdin, sys.stdout, dz)
 
def error(msg):
    sys.stderr.write("Error: %s\n" % msg)
    raise SystemExit
 
def stl_shift_z_filenames(file_in, file_out, dz):
    if not os.path.exists(file_in):
        # Another option is to return an error code or raise
        # a more specific exception
        error("%s does not exists" % file_in)
    if os.path.exists(file_out):
        error("%s exists, not overwriting" % file_out)
    with open(file_in, 'r') as fd_in:
        with open(file_out, 'w+') as fd_out:
            stl_shift_z_streams(fd_in, fd_out, dz)
 
def stl_shift_z_streams(input_stream, output_stream, dz):
    for l in input_stream:
        if 'vertex' in l:
            parts = l.rsplit(' ', 1)
            output_stream.write(parts[0] + ' ' + str(float(parts[1]) + dz) + '\n')
        else:
            output_stream.write(l)
 
if __name__ == '__main__':
    main()
