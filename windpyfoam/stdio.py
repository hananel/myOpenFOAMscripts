def warn(x):
    print "WARNING:", x

def debug(x):
    print "DEBUG:", x

def status(x):
    print "STATUS:", x

def run(f, kw):
    f(**kw)
