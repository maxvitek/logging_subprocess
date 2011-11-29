# Code borrowed from http://stackoverflow.com/questions/6809590/merging-a-python-scripts-subprocess-stdout-and-stderr-while-keeping-them-disti/6810231#6810231
import subprocess
import select
from logging import DEBUG, ERROR


def call(popenargs, logger, stdout_log_level=DEBUG, stderr_log_level=ERROR, **kwargs):
    """
    Variant of subprocess.call that accepts a logger instead of stdout/stderr,
    and logs stdout messages via logger.debug and stderr messages via
    logger.error.
    """
    child = subprocess.Popen(popenargs, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, **kwargs)
    poll = select.poll()
    poll.register(child.stdout, select.POLLIN | select.POLLHUP)
    poll.register(child.stderr, select.POLLIN | select.POLLHUP)
    pollc = 2
    events = poll.poll()
    while pollc > 0 and len(events) > 0:
        for rfd, event in events:
            if event & select.POLLIN:
                if rfd == child.stdout.fileno():
                    line = child.stdout.readline()
                    if len(line) > 0:
                        logger.log(stdout_log_level, line[:-1])
                if rfd == child.stderr.fileno():
                    line = child.stderr.readline()
                    if len(line) > 0:
                        logger.log(stderr_log_level, line[:-1])
            if event & select.POLLHUP:
                poll.unregister(rfd)
                pollc -= 1
            if pollc > 0:
                events = poll.poll()
    return child.wait()

# tests, plunked in here for convenience

import sys
import unittest2
import logging_subprocess
import logging
from StringIO import StringIO


class LoggingSubprocessTest(unittest2.TestCase):
    def setUp(self):
        self.buffer = StringIO()
        self.logger = logging.getLogger('logging_subprocess_test')
        self.logger.setLevel(logging.DEBUG)
        self.logHandler = logging.StreamHandler(self.buffer)
        formatter = logging.Formatter("%(levelname)s-%(message)s")
        self.logHandler.setFormatter(formatter)
        self.logger.addHandler(self.logHandler)

    def test_log_stdout(self):
        logging_subprocess.call([sys.executable, "-c",
                                "print 'foo'"], self.logger)
        self.assertIn('DEBUG-foo', self.buffer.getvalue())

    def test_log_stderr(self):
        logging_subprocess.call([sys.executable, "-c",
                                'import sys; sys.stderr.write("foo\\n")'],
                                self.logger)
        self.assertIn('ERROR-foo', self.buffer.getvalue())

    def test_custom_stdout_log_level(self):
        logging_subprocess.call([sys.executable, "-c",
                                "print 'foo'"], self.logger,
                                stdout_log_level=logging.INFO)
        self.assertIn('INFO-foo', self.buffer.getvalue())

    def test_custom_stderr_log_level(self):
        logging_subprocess.call([sys.executable, "-c",
                                'import sys; sys.stderr.write("foo\\n")'],
                                self.logger,
                                stderr_log_level=logging.WARNING)
        self.assertIn('WARNING-foo', self.buffer.getvalue())

if __name__ == "__main__":
    unittest2.main()
