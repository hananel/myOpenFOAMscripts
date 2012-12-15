#!/usr/bin/env python

__version__ = '0.0.1'

import os

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from flask import Flask, jsonify, send_file, render_template

# configure matplotlib, our plotting backend, to use Agg
import matplotlib
matplotlib.use('Agg')

from twisted_windpy import ProcessManager

class Web(object):
    """ not used """
    def __init__(self):
        self._warn = []
        self._debug = []
        self._status = []

    def warn(self, x):
        self._warn.append(x)

    def debug(self, x):
        self._debug.append(x)

    def status(self, x):
        self._status.append(x)

class WindPyFoamApp(Flask):
    def __init__(self):
        Flask.__init__(self, 'windpyfoam')
        self.process_manager = ProcessManager()

app = WindPyFoamApp()
app.debug = True

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/status')
def status():
    """ return json """
    status = app.process_manager.get_status()
    # NOTE: without enumerate json will clobber.
    return jsonify(enumerate(status))

# TODO: replace pdf usage with plot viewer, using the actual
# data instead of rendering on the server.
@app.route('/results.pdf')
def results():
    if os.path.isfile('results.pdf'):
        r =  send_file('results.pdf')
        #print "DEBUG: %s" % repr(r)
        return r
    return 'missing results.pdf'

@app.route('/launch')
def launch():
    if app.process_manager.process_count() > 0:
        return 'process running'
    else:
        if not app.process_manager.start_process('windPyFoamDict'):
            return 'Failed to start process'
        else:
            # TODO - for specific process
            # TODO - use template
            return 'success'

def run(port=8880):
    print "running windpyfoam web server %s" % __version__
    print "listening on port %s" % port
    root = WSGIResource(reactor, reactor.getThreadPool(), app)
    factory = Site(root)
    reactor.listenTCP(port, factory)
    reactor.run()

if __name__ == '__main__':
    run()
