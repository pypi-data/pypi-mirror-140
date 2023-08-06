"""init
"""

_setup_ = {
    'version' : '0.9.0',
    'description' : 'Create an empty cliq workspace'
}

import sys
from cliq.main.command import SimpleCommand
from cliq.core.init import Init

def init(app):
    return InitCommand(app)

class InitCommand(SimpleCommand):
    def __init__(self, app, name='init'):
        super().__init__(app, name)

    def run(self, argv):
        try:
            Init(self.app.name, self.app.cwd)
        except Exception as e:
            sys.exit(str(e))
