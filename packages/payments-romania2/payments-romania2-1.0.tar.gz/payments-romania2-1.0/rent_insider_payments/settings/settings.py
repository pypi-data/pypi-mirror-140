from .common import *

APPLICATION_ENV = env('ENVIRONMENT')

if APPLICATION_ENV == 'production':
    from .production import *
elif APPLICATION_ENV == 'staging':
    from .staging import *
elif APPLICATION_ENV == 'ci':
    from .ci import *
else:
    from .local import *
