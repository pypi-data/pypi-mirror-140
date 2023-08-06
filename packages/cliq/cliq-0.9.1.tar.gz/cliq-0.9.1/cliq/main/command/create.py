"""create:
"""

_setup_ = {
    'description' : 'create',
    'version' : '0.9.0'
}

__epilog__ = """
example:
  # create a new project
  $ cliq create project ./myapp

  # create a new command 
  $ cliq create command do.py
  $ python do.py
"""

TEMPLATE_PARSER = """
        {name}_parser = self.add_parser('{name}', help='{name}')
        # add arguments, for example:
        #
        # {name}_parser.add_argument('arg', type=str, nargs='*', help='arg')
        # {name}_parser.add_argument('-q', '--quickly', action='store_true', help='quickly')
        # 
        {name}_parser.set_defaults(func='{name}')
"""

TEMPLATE_FUNCTION = """
    def {name}(self, args):
        # implement the function for the subcommand {name}
        print(args)

"""



import sys
import shutil
import pathlib
from cliq.main.command import ComplexCommand
import cliq.templates.command
import cliq.templates.project
import cliq.templates.library
import cliq.templates.module

def init(app):
    return Command(app)

class Command(ComplexCommand):
    def __init__(self, app = None, name = 'create'):
        super().__init__(app, name, epilog = __epilog__)

        project_parser = self.add_parser('project', help='create a project')
        project_parser.add_argument('path', type=str, help='project path')
        #project_parser.add_argument('--standalone', action='store_true', help='standalone')
        project_parser.add_argument('--cli', '--with-cli', type=str, 
                                    help='a list of command line interface modules separate by commas')

        project_parser.add_argument('--description', type=str, help='description in setup.py')
        project_parser.add_argument('--keywords', type=str, help='keywords in setup.py')
        project_parser.add_argument('--author', type=str, help='author in setup.py')
        project_parser.add_argument('--email', type=str, help='author_email in setup.py')
        project_parser.add_argument('--url', type=str, help='url in setup.py')
        project_parser.add_argument('--license', type=str, help='license in setup.py')
        
        project_parser.set_defaults(func='project')

        module_parser = self.add_parser('module', help='add a cli module')
        module_parser.add_argument('path', help='module path')
        module_parser.set_defaults(func='module')

        command_parser = self.add_parser('command', help='create a command')
        command_parser.add_argument('filename', type=str, help='a command script filename')
        command_parser.add_argument('--sub', '--subcommands', '--with-subcommands',
                                    type=str,
                                    help='a list of subcommands separated by commas')
        command_parser.add_argument('--desc', '--description', type=str,
                                    help='description')
        command_parser.set_defaults(func='command')

    def project(self, args):
        # project info
        description = args.description if args.description is not None else ''
        keywords = args.keywords if args.keywords is not None else ''
        author = args.author if args.author is not None else ''
        author_email = args.email if args.email is not None else ''
        url = args.url if args.url is not None else ''
        license = args.license if args.license is not None else ''


        # paths
        project_path = pathlib.Path(args.path)
        lib_path = project_path / project_path.name
        project_name = lib_path.stem

        # make project directory and create commandl line modules
        # if there are requested multiple command line modules,
        #    create <project/project> (the top-level package directory)
        #    and create command line modules <project/project/cli/main/command>
        #        for each cli in cli_names
        # else
        #    create <project/project/main/command>
        if args.cli is None:
            cli_names = [project_name]
            self.__create_library(lib_path)
            self.__create_module(lib_path)
        else:
            cli_names = args.cli.split(',')
            self.__create_library(lib_path)
            for modname in cli_names:
                mod_path = lib_path / modname
                self.__create_module(mod_path)

        # find templates directory
        templates_project_path = pathlib.Path(cliq.templates.project.__path__[0])
        
        # generate setup.cfg
        with open(templates_project_path / 'setup.cfg') as file:
            setup_cfg = file.read()
        with open(project_path / 'setup.cfg', 'w') as file:
            file.write(setup_cfg)

        # generate setup.py
        if len(cli_names) == 1:
            template = "'{cli}={project}.main:main'"
        else:
            template = "'{cli}={project}.{cli}.main:main'"

        console_scripts = ','.join([template.format(project=project_name, cli=cli_name)
                                    for cli_name in cli_names])

        with open(templates_project_path / 'setup.py') as file:
            setup_py = file.read()
        with open(project_path / 'setup.py', 'w') as file:
            file.write(setup_py.format(name=project_name,
                                       description=description,
                                       keywords=keywords,
                                       author=author,
                                       author_email=author_email,
                                       url=url,
                                       license=license,
                                       console_scripts=console_scripts))
       
        # generate README.md
        with open(project_path / 'README.md', 'w') as file:
            file.write('# {name}\n'.format(name=project_name))
        
    def __create_library(self, lib_path):
        # create the top-level package directory and generate __init__.py
        # where multiple command line modules will be created.
        lib_path.mkdir(parents=True)

        # generate __init__.py
        templates_library_path = pathlib.Path(cliq.templates.library.__path__[0])
        with open(templates_library_path / '__init__.py') as file:
            top_init_py = file.read()

        with open(lib_path / '__init__.py', 'w') as file:
            file.write(top_init_py.format(cliq_version=self.app.version, name=lib_path.stem))
        
    def __create_module(self, module_path):
        # create a command line module and generate files
        
        # paths
        main_path = module_path / 'main'
        command_path = main_path / 'command'
        
        # 
        try:
            command_path.mkdir(parents=True)
        except FileExistsError:
            sys.exit("fatal: '{}' already exists within destination path '{}'"
                     .format(command_path, module_path))
        
        # path to cliq/templates/module
        templates_module_path = pathlib.Path(cliq.templates.module.__path__[0])

        # generate __init__.py for module
        with open(templates_module_path / '__init__.py') as file:
            module_init_py = file.read()

        with open(module_path / '__init__.py', 'w') as file:
            file.write(module_init_py.format(cliq_version=self.app.version, name=module_path.stem))

        # generate __init__.py for main
        with open(templates_module_path / 'main' / '__init__.py') as file:
            main_init_py = file.read()

        with open(module_path / 'main' / '__init__.py', 'w') as file:
            file.write(main_init_py.format(cliq_version=self.app.version))

        # copy command files
        dest_path = module_path / 'main' / 'command' 
        for src in (templates_module_path / 'main' / 'command').glob('*.py'):
            shutil.copy(src, dest_path)






    def module(self, args):
        mod_path = pathlib.Path(args.path)
        #if mod_path.exists():
        #    sys.exit("fatal: destination path '{}' already exists.".format(args.path))
            
        self.__create_module(mod_path)

    def command(self, args):
        path = pathlib.Path(args.filename)
        command_name = path.stem
        desc = args.desc if args.desc is not None else ''
        
        if path.exists():
            sys.exit("fatal: file '{}' already exists.".format(args.filename))
            
        path.parent.mkdir(parents=True, exist_ok=True)
        
        templates_command_path = pathlib.Path(cliq.templates.command.__path__[0])

        if args.sub is None:
            with open(templates_command_path / 'simple.py') as file:
                temp = file.read()

                content = temp.format(name=command_name, description=desc)
        else:
            with open(templates_command_path / 'complex.py') as file:
                temp = file.read()

            subs = args.sub.split(',')
            code_parsers = ''
            code_funcs = ''
            for sub in subs:
                code_parsers += TEMPLATE_PARSER.format(name=sub)
                code_funcs += TEMPLATE_FUNCTION.format(name=sub)

            content = temp.format(name=command_name, description=desc,
                                  parsers=code_parsers, funcs=code_funcs)

        with open(path, 'w') as file:
            file.write(content)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = PleaseCommand()
    command.run(argv)

if __name__ == '__main__' :
    main()
