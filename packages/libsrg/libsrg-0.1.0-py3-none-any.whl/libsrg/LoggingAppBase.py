#!/usr/bin/env  python3

import argparse
import logging

import libsrg


class LoggingAppBase:
    """This base class initializes the logger and creates a minimal argparse command line parser in __init__
    The parser is not run in this call. The application code can then add arguments to the parser.
    Since calls to derived class functions can not be made in the base class constructor, this must be done
    in separate steps.

    After augmenting the parser, the application code should call perform_parse after adding arguments to the
    parser before attempting to access the parsed results.

    https://docs.python.org/3/howto/argparse.html

     """

    # note that
    logger = logging.getLogger("libsrg.LoggingAppBase")

    def __init__(self,level=logging.INFO,logfile=None):
        libsrg.LoggingCounter.config_and_attach()
        self.args = {}
        self.initial_level=level
        try:
            usage = "usage: %prog [options]"
            self.parser = argparse.ArgumentParser(usage)
            self.parser.add_argument('-v', '--verbose', help='enable verbose output', dest='verbose',
                                     action='store_true',
                                     default=False)
            self.parser.add_argument('--logfile', help='file to log to (default = stdout)', dest='logfile',
                                     type=str, default=logfile)
        except Exception as e:
            self.logger.exception(f"Unexpected exception: {e}")
            raise e

    def perform_parse(self):
        self.args = self.parser.parse_args()
        if self.args.verbose:
            log_level = logging.DEBUG
        else:
            log_level = self.initial_level
        logging.getLogger().setLevel(log_level)
        if 'logfile' in self.args and self.args.logfile is not None:
            libsrg.LoggingCounter.add_logfile(self.args.logfile, mode='w')


"""
This is just a simple demo application to show how the LoggingAppBase class should be extended.

It serves no real purpose other than serving as a regression test.

pytest mucks with logging before running test code
"""


class SampleApp(LoggingAppBase):
    logger = logging.getLogger("libsrg.SampleApp")

    def __init__(self):
        LoggingAppBase.__init__(self)
        self.logger.info("before adding args")
        # setup any program specific command line arguments
        self.parser.add_argument('--zap', help="Zap something", dest='zap', action='store_true', default=False)
        self.parser.add_argument('--zip', help="Zip something", dest='zip', action='store_true', default=False)
        # invoke the parser
        self.perform_parse()
        #
        self.logger.info(f"after parsing {self.args}")

    def demo_levels(self):
        ctr = libsrg.LoggingCounter.get_instance()
        self.logger.info(f"getEffectiveLevel is {self.logger.getEffectiveLevel()}  logging.INFO={logging.INFO}")
        oldcount = ctr.count_for_level(logging.DEBUG)
        self.logger.info("call to debug below will be suppressed")
        self.logger.debug("debug log wont show or count this line")
        newcount = ctr.count_for_level(logging.DEBUG)
        assert oldcount == newcount
        self.logger.setLevel(logging.DEBUG)
        self.logger.info("Changed level to DEBUG")
        self.logger.info(f"getEffectiveLevel is {self.logger.getEffectiveLevel()} logging.DEBUG={logging.DEBUG}")
        self.logger.debug("This should show and count")
        newcount = ctr.count_for_level(logging.DEBUG)
        assert (oldcount + 1) == newcount

    def demo_runner(self):
        self.logger.warning("A warning")
        try:
            # linux with systemd assumed in self-test
            #   this is just an external command with multiple lines of output
            r = libsrg.Runner(["hostnamectl"])
            self.logger.info(r)
            r2 = libsrg.Runner(["missing program trapped exception"])
            self.logger.info(r2)
            r3 = libsrg.Runner(["missing program rethrow exception"], rethrow=True)
            self.logger.info(r3)
        except Exception as ex:
            self.logger.info("VVVVV Exception optionally propagated to calling program")
            self.logger.critical(ex, exc_info=True)
            self.logger.info("^^^^^ that was supposed to throw an exception")

    def demo_final_checks(self):
        ctr = libsrg.LoggingCounter.get_instance()
        self.logger.info("Asserts check actual versus expected logging counts as logged at end of run (atexit)")
        self.logger.info("  note that counters are frozen in atexit code, so atexit output does not change counts\n\n")
        assert ctr.count_for_level(logging.CRITICAL) == 1
        assert ctr.count_for_level(logging.ERROR) == 2
        assert ctr.count_for_level(logging.WARNING) == 1
        assert ctr.count_for_level(logging.DEBUG) == 1
        assert ctr.count_for_level(logging.INFO) == 13

    @classmethod
    def demo(cls):
        app = SampleApp()
        app.demo_levels()
        app.demo_runner()
        app.demo_final_checks()


if __name__ == '__main__':
    SampleApp.demo()
