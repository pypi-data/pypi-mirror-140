import logging
#logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s:%(module)s: %(message)s',
        },
        'flask': {
            'format': '%(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'flask'
        },
        'stderr-handler': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'default'
        },
        'dgenies-handler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/dgenies.log',
            'when': 'W6',
            'interval': 1,
            'formatter': 'default'
        },
        'local-scheduler-handler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/local-scheduler.log',
            'when': 'W6',
            'interval': 1,
            'formatter': 'default'
        }
    },
#    'root': {
#        'level': 'INFO',
#        'handlers': ['dgenies-app']
#    },
    'loggers': {
        'flask.app': {
            'level': 'INFO',
            'handlers': ['wsgi']
        },
        'dgenies': {
            'level': 'INFO',
            'handlers': ['stderr-handler', 'dgenies-handler']
        },
        'local_scheduler': {
            'level': 'INFO',
            'handlers': ['stderr-handler', 'local-scheduler-handler']
        }
    },
})