"""{name}: {description}
"""

_setup_ = {{
    'version' : '0.0.0',
    'description' : '{description}',
}}

import sys
from cliq.main.command import SimpleCommand

def init(app):
    return Command(app)

class Command(SimpleCommand):
    def __init__(self, app = None, name = __name__):
        super().__init__(app, name)

        # self.parser is an argparse.ArumentParser
        # see https://docs.python.org/3/library/argparse.html       
        #
        # add arguments. for example:
        #
        # self.parser.add_argument('input', type=str, help='input filename')
        # self.parser.add_argument('-v', '--verbose', action='store_true', help='verbose')
        # self.parser.add_argument('-o', '--output', type=str, help='output filename')

    def run(self, argv):
        args = self.parser.parse_args(argv)

        # implement command line functionalities
        print(args)
 
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = Command()
    command.run(argv)

if __name__ == '__main__' :
    main()
