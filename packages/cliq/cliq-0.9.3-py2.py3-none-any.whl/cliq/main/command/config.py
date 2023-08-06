"""config
"""

_setup_ = {
    'version' : '0.8.0',
    'description' : 'Get and set local (workspace) or global (user) options'
}

__epilog__ = """
example:

  $ cliq config user.name yourname
  $ cliq config --global user.name yourname
  $ cliq config --list
  $ cliq config --global --list
  $ cliq config --local --list
  $ cliq config --unset user.name
  $ cliq config --global --unset user.name
"""

import sys
from cliq.main.command import SimpleCommand
from cliq.core.config import Config

def init(app):
    return ConfigCommand(app)

class ConfigCommand(SimpleCommand):
    def __init__(self, app, name=__name__):
        super().__init__(app, name, epilog = __epilog__.replace('cliq', app.name))


        # config name value
        self.parser.add_argument('name', type=str, nargs='?')
        self.parser.add_argument('value', type=str, nargs='?')

        ## list, unset, add, get;
        ## rename-section, remove-section
        self.parser.add_argument('-l', '--list', action='store_true', help='list all options')
        self.parser.add_argument('--unset', action='store_true', help='remove a variable: name')
               
        ## local, global
        location_group = self.parser.add_mutually_exclusive_group()
        location_group.add_argument('--global', action='store_true', help='use global config file')
        location_group.add_argument('--local', action='store_true', help='use local config file')

        ## show-origin, show-scope
        # self.parser.add_argument('--show-origin', action='store_true',
        #                         help='show origin of config (file)')
        # self.parser.add_argument('--show-scope', action='store_true',
        #                         help='show scope of config (local, global)')

    def run(self, argv):

        args = self.parser.parse_args(argv)
        
        try:
            config = self.app.config
        except Exception as e:
            sys.exit(str(e))
            

        if args.list :
            if args.name is not None or args.value is not None:
                print('error: wrong number of arguments, should be 0')
                self.parser.print_help()
                
                if getattr(args, 'global') :
                    config = self.app.config.global_config
                elif args.local:
                    config = self.app.config.local_config


            # self.app.config.finder.global_config_filename
            # self.app.config.finder.local_config_filename

            for secname in config.sections():
                for name in config[secname]:
                    print(secname + '.' + name + '=' + config[secname][name])
        elif args.name is not None:
            try:
                section, name = args.name.split('.')
            except ValueError:
                sys.exit('error: key does not contain a section: {}'.format(args.name))

            if args.unset:
                if args.value is None:
                    if getattr(args, 'global'):
                        config.unset_global(section, name, args.value)
                    else:
                        try:
                            config.unset_local(section, name, args.value)
                        except OSError:
                            sys.exit('fatal: not in a {} directory'.format(self.app.name))
                else:
                    print('error: wrong number of arguments, should be 1')
                    self.parser.print_help()
            else:
                if args.value is None:    
                    print(config[section][name])
                else:
                    if getattr(args, 'global'):
                        config.set_global(section, name, args.value)
                    else:
                        try:
                            config.set_local(section, name, args.value)
                        except OSError:
                            sys.exit('fatal: not in a {} directory'.format(self.app.name))
        else:
            self.parser.print_help()
