#!/usr/bin/env python

__version__ = '0.0.1'

import os

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource

from flask import Flask, jsonify, send_file

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
    return """<html>
<head>
    <title>WindPyFoam</title>
</head>
<body>
<p>
Welcome to windpyfoam!
</p>
<p>
<a href="/launch">click to launch simulation</a>
</p>
</body>
</html
"""

process_reader = """<html>
<head>
<title>process viewer</title>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
<script>
function startUpdateStatus() {
    $.getJSON("/status", {}, function(json) {
        $("#status").append(JSON.stringify(json));
        //var data = JSON.parse(json, function(k, v) {
        //    $("#status").append("<div>" + k + " " + v + "</div>");
        //});
    });
    setTimeout(startUpdateStatus, 1000);
}
$(document).ready(function () {
    $("#status").append("started");
    startUpdateStatus();
})
</script>
</head>
<body>
<div id="status">
</div>
</body>
</html>
"""

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
            return process_reader

def run():
    root = WSGIResource(reactor, reactor.getThreadPool(), app)
    factory = Site(root)
    reactor.listenTCP(8880, factory)
    reactor.run()

if __name__ == '__main__':
    print "running windpyfoam web server %s" % __version__
    run()
