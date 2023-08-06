"""please: a toy complex command
"""

_setup_ = {
    'description' : 'a toy complex command',
    'version' : '0.1.0'
}

import sys
from cliq.main.command import ComplexCommand

def init(app):
    return PleaseCommand(app)

class PleaseCommand(ComplexCommand):
    def __init__(self, app = None, name = 'please'):
        super().__init__(app, name)

        say_parser = self.add_parser('say', help='say something')
        say_parser.add_argument('something', type=str, help='something')
        say_parser.add_argument('-f', '--format', type=str, default='text/plain', help='format')
        say_parser.set_defaults(func='say')
        
        sum_parser = self.add_parser('sum', help='sum numbers')
        sum_parser.add_argument('numbers', type=float, nargs='+', help='numbers')
        sum_parser.set_defaults(func='sum')

    def say(self, args):
        print(args.something)

    def sum(self, args):
        print(sum(args.numbers))

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = PleaseCommand()
    command.run(argv)

if __name__ == '__main__' :
    main()
