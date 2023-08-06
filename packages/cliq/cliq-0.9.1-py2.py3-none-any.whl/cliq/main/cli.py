"""cliq command line tool.


Variables:

- argv : list of string (from sys.argv[1:])
- args : Namespace object returned (from argparser.ArgumentParser.parse_args())

"""

import sys
import os
import subprocess
import argparse

import cliq
from cliq.main import commander
from cliq.core.config import Config, ConfigFinder


class App(object):
    def __init__(self, package):
        """
        package: package name. eg) <myapp>.main or <mylib>.<mycli>.main
        """
        self.__package__ = package
        self.name = package.split('.')[-2]
        
        try:
            modname = '.'.join(package.split('.')[:-1])   # <myapp> or <mylib>.<mycli>
            mod = __import__(modname, fromlist=['main'])
            self.version = mod.__version__                
        except Exception as e:
            try:
                # get __version__ from the top level package
                mod = __import__(package)                  # mod is the top level package
                self.version = mod.__version__
            except:
                self.version = 'unknown'

        self.critical_failure = False 
        self.errors = []
        self.warnings = []

        self.cwd = os.getcwd()
        
        self.commander = commander.Commander(self)

        self.__config = None

    @property
    def config(self):
        if self.__config is None:
            try:
                self.__config = Config(self.name, self.cwd)
            except:
                raise Exception('fatal: not a {} workspace (or any of the parent directories): .{}'.format(self.app.name, self.app.name))
            
        return self.__config
        
    def run(self, argv=None):
        if argv is None:
            argv = sys.argv[1:]
            
        self.commander.run(argv)

    def exit(self):
        """Exits the program. Checks errors and warnings.
        """
        pass


def main(argv=None):
    """entry-point for console-script
    """
    if argv is None:
        argv = sys.argv[1:]

    app = App(__package__)
    app.run(argv)
    app.exit()
       
if __name__ == '__main__':
    main()

