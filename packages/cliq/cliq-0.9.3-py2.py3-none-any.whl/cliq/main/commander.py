# commander.py
#
# command center
#
import argparse
import os
import sys
import pkgutil

class Commander:
    """Commander: parse arguments and dispatch commands
    """
    def __init__(self, app):
        self.app = app
        
        # parser
        self.parser = argparse.ArgumentParser(prog=self.app.name, add_help=False)
        self.parser._positionals.title = 'arguments'
        self.parser.add_argument('--help', action='store_true')      # <cliq> --help
        self.parser.add_argument('--version', action='store_true')   # <cliq> --version
        self.subparsers = self.parser.add_subparsers(title='commands', help='command help')
        
    def parse_args(self, argv):

        # check argv and register commands. a command should be the first argument 
        #
        # $ <myapp> <mycom> xxx ... => register <myapp>.main.command.<mycom>
        #
        # check if exists <module>/main/command/__init__.py
        #          and __init__.py defines a cliq command.
        pkg = __import__(self.app.__package__ + '.command', fromlist=[''])
 
        if not hasattr(pkg, 'main') and not hasattr(pkg, 'init'):
            self.parser.set_defaults(command='help')
            return self.__parse_args(argv)
        else:
            self.__parse_args_with_main_command(pkg, argv)
            sys.exit(0)

    def __parse_args(self, argv):
        # this method will process argv
        # if not exists <module>/main/command/__init__.py
        #    or __init__.py does not contains a proper cliq command
        
        if len(argv) > 0 and not argv[0].startswith('-'):
            command = argv[0]
            try: 
                mod = __import__(self.app.__package__ + '.command.' + command, fromlist=[''])
                if hasattr(mod._setup_, 'description'):
                    self.add_command_parser(command, help=mod._setup_['description'])
                else:
                    self.add_command_parser(command)
            except ModuleNotFoundError:
                sys.exit("{app}: '{com}' is not a {app} command. See '{app} --help'"
                         .format(app=self.app.name, com=command))
                   
                
        # Use parse_known_args() to pass -h|--help option to the subparsers.
        # parse_args() takes -h|--help and immediately print help and exit the
        # program.

        args, argv = self.parser.parse_known_args(argv)   # pass -h|--help
        return args

    def __parse_args_with_main_command(self, main_command_pkg, argv):
        # this method will process argv
        # if exists <module>/main/command/__init__.py
        #    and __init__.py contains a cliq command
        #
        # main_command_pkg is the <module>.main.command package
        # main_command_pkg.init is the method defined in <module>/main/command/__init__.py
        main_command = main_command_pkg.init(self.app)
        
        # change <ArgumentParser>.prog from 'myapp command' to 'myapp'
        main_command.parser.prog = self.app.name  

        # try to parse argv with self.parser
        # argv may contain a proper command or --help or --version
        if len(argv) > 0 and (not argv[0].startswith('-') or argv[0] == '--help' or argv[0] == '--version'):
            try:
               args = self.__parse_args(argv)
            except:
                args = None
        else:
            args = None
                
            
        if args and args.help:
            self.__print_help_with_main_command(main_command)
        elif args and args.version:
            self.print_version()
            sys.exit()
        elif hasattr(args, 'command'):
            mod = __import__(self.app.__package__ + '.command.' + args.command, fromlist=[''])
            command = mod.init(self.app)
            command.run(argv[1:]) # args.subargv
            sys.exit(0)
        else:
            try:   
                main_command.run(argv)
            except:
                #self.__print_help_with_main_command(main_command)
                os._exit(0)

    def __print_help_with_main_command(self, main_command):
        main_command.parser.print_help()
        print()
        print('WITH PREDEFINED COMMANDS')
        print('========================\n')
        self.print_help()

    def run(self, argv):

        args = self.parse_args(argv)

        if args.help:
            self.print_help()
        elif args.version:
            self.print_version()
        elif args.command == 'help' and not hasattr(args, 'subargv'):
            self.print_help()
        else:
            mod = __import__(self.app.__package__ + '.command.' + args.command, fromlist=[''])
            command = mod.init(self.app)
            command.run(argv[1:]) # args.subargv

    def add_command_parser(self, command: str, help: str = ''):
        """
        Add a subparser for `<cliq> <command>`. For example, `<cliq> please`
        ```
        commander.add_command_parser('please', help='please command')
        ```
        """
        subparser = self.subparsers.add_parser(command, help=help, add_help=False)

        # prevent parsing subarguments
        subparser.add_argument('subargv', type=str, nargs=argparse.REMAINDER)
        subparser.set_defaults(command=command)
        
        return subparser

    def print_version(self):
        print(self.app.name, 'version', self.app.version)

    def print_help(self):
        self._register_commands()
        self.parser.print_help()

    def _register_commands(self):
        """registers all modules from <cliq>.main.command to self.subparsers
        """
        pkg = __import__(self.app.__package__ + '.command', fromlist=[''])
        for module_info in pkgutil.iter_modules(pkg.__path__):
            if module_info.name not in self.subparsers.choices :
                mod = __import__(self.app.__package__ + '.command.' + module_info.name, fromlist=[''])
                try:
                    self.add_command_parser(module_info.name, help=mod._setup_['description'])
                except AttributeError:
                    self.add_command_parser(module_info.name)

       
        
        

