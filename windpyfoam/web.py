from flask import Flask

from twisted_windpy import ProcessManager

class Web(object):
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

web = Web()

app = Flask('windpyfoam')
@app.route('/')
def hello():
    return """<html>
<head><title>WindPyFoam</title</head>
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

@app.route('/run')
def launch():
    if app.process_manager.process_count() > 0:
        return 'process running'
    else:
        app.process_manager.start_process()
        return 'started process'

def run(f, args):
    app.process_manager = ProcessManager()
    app.run()

def test_flask():
    run()

if __name__ == '__main__':
    print "Testing Flask"
    test_flask()
