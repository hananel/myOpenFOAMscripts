from flask import Flask

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
    return "Hello World!"

def run(f, args):
    app.run()

def test_flask():
    run()

if __name__ == '__main__':
    print "Testing Flask"
    test_flask()
