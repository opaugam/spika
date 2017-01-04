import json
from subprocess import Popen, PIPE
import sys
from threading import Event, Lock, Thread
import time

__version__ = '1.0.0'


class BadExit(Exception):
    """
    Exception raised if ever the subprocess exits on anything other than 0
    """
    def __init(code):
        self.code = code


class driven:
    """
    Simple context manager that spawns a subprocess and allows to exchange
    commands via stdin/stdout piping. The commands are simple strings and
    may be decorated with extended payload. The subprocess reads those
    commands on its stdin as serialized json and must write a response back
    on its stdout.

    The json payload contains a unique identifier that must be included in
    the response.
    """

    def __init__(self, cmd, cwd='.', env={}):
        #
        # - popen our subprocess and pipe its stdin/stdout
        #
        self.sub = Popen(cmd.split(' '), close_fds=True, bufsize=1,
                         cwd=cwd, env=env, stdin=PIPE, stdout=PIPE)
        self.cnt = 0
        self.lck = Lock()
        self.events = {}
        self.code = 0

        def _out(fd, lock, events):
            for line in iter(fd.readline, b''):
                try:
                    print line
                    js = json.loads(line)
                    if not 'tag' in js or not 'ext' in js:
                        continue

                    tag = js['tag']
                    with lock:
                        if tag in events:
                            #
                            # - we matched an existing event in our dict
                            # - trigger the event and re-key using the
                            #   decoded json response
                            #
                            event = events[tag]
                            events[tag] = js
                            event.set()

                except ValueError:
                    pass

            #
            # - the subprocess exited
            # - set all remaining events to None
            #
            with lock:
                for tag, event in self.events.items():
                    events[tag] = None
                    event.set()
        #
        # - start piping stdout
        #
        args = (self.sub.stdout, self.lck, self.events)
        self.out = Thread(target=_out, args=args)
        self.out.start()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        #
        # - at this point the subprocess should have exited gracefully
        # - if not terminate and wait for it
        #
        if self.sub.returncode is None:
            self.sub.kill()
            self.sub.wait()
        #
        # - join our inner thread
        # - pass any exception at that point or raise if the subprocess didn't
        #   exit cleanly
        #
        self.out.join()
        if type is not None:
            return False
        elif self.sub.returncode != 0:
            raise BadExit(self.sub.returncode)
        else:
            return True

    def ask(self, cmd, ext={}, timeout=None):
        #
        # - get a new unique sequence number (just increment an integer)
        # - key it in our dict with a new event instance
        # - include the optional json payload if specified
        #
        with self.lck:
            tag = self.cnt
            self.cnt += 1

        try:
            #
            # - prep our little json command
            # - serialize to json and write to the subprocess stdin (don't
            #   forget to add \n as a separator)
            # - wait on our event and rekey with the response unless we
            #   time out
            #
            event = Event()
            js = {'tag': tag, 'cmd': cmd, 'ext': ext}
            self.events[tag] = event
            self.sub.stdin.write(json.dumps(js) + '\n')
            if not event.wait(timeout=timeout):
                return None
            js = self.events[tag]
            return None if js is None else js['ext']

        except IOError:
            #
            # - the subprocess died and we can't write to the pipe, simply fail
            #   on a None
            #
            return None

        finally:
            #
            # - make sure we lock and cleanup the dict
            # - locking is required to avoid a race condition where the _out
            #   thread updates the dict after cleanup therefore leaking
            #   entries
            #
            with self.lck:
                del self.events[tag]