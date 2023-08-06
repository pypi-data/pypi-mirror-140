"""config
"""

_setup_ = {
    'version' : '0.0.1',
    'description' : 'Get and set local (workspace) or global (user) options'
}

import cliq.main.command.config

def init(app):
    return cliq.main.command.config.init(app)

