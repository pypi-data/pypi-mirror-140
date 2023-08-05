import logging
import subprocess

"""
Runner is a utility class to run a command as a subprocess and return results
* command is passed as a list of program followed by zero or more arguments
* Runner objects are single use
  * command executed by constructor
  * results returned as fields of object
* stdout and stderr are captured and returned as lists of utf-8 strings
  * one list element per line
  * end of line chars removed
  * empty list if no output captured
* return code as integer
* any exception raised is caught
  * returned in caught field
  * logged as an error
  * optionally rethrown if rethrow is set True
* success field is true if no exceptions caught and return code is zero
"""


class Runner():
    logger = logging.getLogger("libsrg.Runner")

    def __init__(self, cmd: list[str], timeout=None, rethrow=False):
        # cmd is a list of program name and zero or mor eorguments
        # timeout (if specified) is a timeout to communicate in seconds
        self.cmd = cmd
        self.success = False
        self.so_bytes: bytearray
        self.se_bytes: bytearray
        self.ret: int = -1
        self.so_lines: list[str] = []
        self.se_lines: list[str] = []
        self.caught: Exception = None
        self.p = None
        self.rethrow = rethrow
        self.execute()

    def execute(self):
        try:
            self.p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (self.so_bytes, self.se_bytes) = self.p.communicate(timeout=3)  # @UnusedVariable
            self.ret = self.p.wait()
            so_str0 = self.so_bytes.decode("utf-8")
            self.so_lines = so_str0.splitlines(keepends=False)
            se_str0 = self.se_bytes.decode("utf-8")
            self.se_lines = se_str0.splitlines(keepends=False)
            self.success = self.ret == 0
        except Exception as ex:
            self.logger.error(ex)
            self.success = False
            self.caught = ex
            if self.rethrow:
                raise ex

    def __str__(self):
        return f'Runner success={self.success} ret={self.ret} cmd={self.cmd}  so_lines={self.so_lines}'
