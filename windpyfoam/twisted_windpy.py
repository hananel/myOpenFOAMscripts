import sys
import os

from twisted.internet import reactor, protocol, task


class WindPyProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, process_manager, i):
        self._process_manager = process_manager
        self._i = i

    def connectionMade(self):
        print "DEBUG: WindPyProcessProtocol.connectionMade"
        #import pdb; pdb.set_trace()

    def childDataReceived(self, fd, data):
        # TODO structured communication
        self._process_manager.on_data(self._i, fd, data)

    def processEnded(self, status):
        self._process_manager.on_process_ended(self._i, status)

class ProcessManager(object):

    def __init__(self):
        self._processes = []
        self._verbose = False
        self._pending_status = []

    def on_data(self, i, fd, data):
        """
        ignore fd for now
        """
        for line in data.split('\n'):
            self._on_line(i, fd, line)

    def get_status(self):
        ret = list(self._pending_status)
        del self._pending_status[:]
        #print "DEBUG: %d" % len(ret)
        return ret

    def _on_line(self, i, fd, line):
        if self._verbose:
            sys.stdout.write("proc %d: %s\n" % (self._processes[i].pid, line))
        # TODO: send to web client not via polling
        # TODO: race here, if process disappears before status is read, i will
        # be invalidated, or worse point to the wrong process.
        if line.startswith('STATUS: '):
            status = line[len('STATUS: '):]
            print "STATUS: (%d) %s" % (len(self._pending_status), status)
            self._pending_status.append((i, status))

    def process_count(self):
        return len(self._processes)

    def start_process(self, dict_filename):
        """
        TODO - give it an stl name
        """
        if not os.path.isfile(dict_filename):
            return False
        try:
            with open(dict_filename) as fd:
                pass
        except:
            return False
        i = len(self._processes)
        self._processes.append(None)
        process_protocol = WindPyProcessProtocol(self, i)
        env = dict(os.environ)
        if 'DISPLAY' not in env:
            print "DEBUG: adding DISPLAY"
            env['DISPLAY'] = ':0.0'
        self._processes[i] = reactor.spawnProcess(process_protocol, '/usr/bin/python',
                ['/usr/bin/python', 'windpyfoam.py', '--dict', dict_filename,
                 '--no-plots'],
                env=env)
        self._processes[i].start_pid = self._processes[i].pid
        return True

    def on_process_ended(self, i, status):
        print self._processes[i].start_pid, "exited"

class TestProcessManager(ProcessManager):
    def on_process_ended(self, i, status):
        super(TestProcessManager, self).on_process_ended(i, status)
        reactor.stop()

class Tester(object):
    def __init__(self):
        self.i = 0
        process_manager = TestProcessManager()
        self.process_manager = process_manager
        process_manager.start_process('windPyFoamDict')
        print process_manager.process_count()
        t = task.LoopingCall(self.cb)
        t.start(1)

    def cb(self):
        status = self.process_manager.get_status()
        if len(status) > 0:
            for i, l in status:
                print i, l

if __name__ == '__main__':
    tester = Tester()
    reactor.run()
