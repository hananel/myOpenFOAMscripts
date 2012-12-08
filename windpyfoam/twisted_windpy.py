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
        self._verbose = True
        self._pending_status = []

    def on_data(self, i, fd, data):
        """
        ignore fd for now
        """
        for line in data.split('\n'):
            self._on_line(i, fd, line)

    def get_status(self):
        ret = self._pending_status[:]
        del self._pending_status[:]
        return ret

    def _on_line(self, i, fd, line):
        if self._verbose:
            sys.stdout.write("proc %d: %s\n" % (self._processes[i].pid, line))
        # TODO: send to web client not via polling
        # TODO: race here, if process disappears before status is read, i will
        # be invalidated, or worse point to the wrong process.
        if line.startswith('STATUS: '):
            status = line[len('STATUS: '):]
            self._pending_status.append((i, status))

    def process_count(self):
        return len(self._processes)

    def start_process(self):
        i = len(self._processes)
        self._processes.append(None)
        process_protocol = WindPyProcessProtocol(self, i)
        self._processes[i] = reactor.spawnProcess(process_protocol, '/usr/bin/python',
                ['/usr/bin/python', 'windpyfoam.py', '--conf', 'windPyFoamDict'],
                env=os.environ)
        self._processes[i].start_pid = self._processes[i].pid

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
        process_manager.start_process()
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
