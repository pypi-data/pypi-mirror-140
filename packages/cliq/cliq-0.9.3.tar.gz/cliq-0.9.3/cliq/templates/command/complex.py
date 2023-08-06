"""{name}: {description}
"""

_setup_ = {{
    'version' : '0.0.0',
    'description' : '{description}',
}}

import sys
from cliq.main.command import ComplexCommand

def init(app):
    return Command(app)

class Command(ComplexCommand):
    def __init__(self, app = None, name = __name__):
        super().__init__(app, name)
        
        # self.add_parser() adds an argparse.ArumentParser
        # see https://docs.python.org/3/library/argparse.html       
 
        {parsers}
        
    {funcs}
    
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = Command()
    command.run(argv)

if __name__ == '__main__' :
    main()
