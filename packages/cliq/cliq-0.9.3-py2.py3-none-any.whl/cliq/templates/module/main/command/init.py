"""init
"""

_setup_ = {
    'version' : '0.0.1',
    'description' : 'Create an empty workspace'
}

import cliq.main.command.init

def init(app):
    return cliq.main.command.init.init(app)

