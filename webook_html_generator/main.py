import logging

from dotenv import load_dotenv
from logging.config import dictConfig
from pathlib import Path
from webook_html_generator.config import Config
from webook_html_generator.generator import Generator
from apscheduler.schedulers.background import BlockingScheduler

LOGGING_CONFIG = {
    'version': 1,
    'loggers': {
        '': {  # root logger
            'level': 'NOTSET',
            'handlers': ['debug_console_handler', 'info_rotating_file_handler', 'error_rotating_file_handler', 'critical_mail_handler'],
        },
        'my.package': {
            'level': 'WARNING',
            'propagate': False,
            'handlers': ['info_rotating_file_handler', 'error_rotating_file_handler'],
        },
    },
    'handlers': {
        'debug_console_handler': {
            'level': 'DEBUG',
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'info_rotating_file_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/info.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        },
        'error_rotating_file_handler': {
            'level': 'WARNING',
            'formatter': 'error',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/error.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 4
        },

        'critical_mail_handler': {
            # TODO implement smtp critical log alert
            'level': 'CRITICAL',
            'formatter': 'error',
            'class': 'logging.handlers.SMTPHandler',
            'mailhost': 'localhost',
            'fromaddr': 'monitoring@wemade.no',
            'toaddrs': ['monitoring@wemade.no', ],
            'subject': 'Critical error with application name'
        }
    },
    'formatters': {
        'info': {
            'format': '%(asctime)s-%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s'
        },
        'error': {
            'format': '%(asctime)s-%(levelname)s-%(name)s-%(process)d::%(module)s|%(lineno)s:: %(message)s'
        },
    },

}

logging.config.dictConfig(LOGGING_CONFIG)


def load_config() -> Config:
    dotenv_path = Path('../.env')
    load_dotenv(dotenv_path=dotenv_path)
    return Config()


if __name__ == '__main__':
    config: Config = load_config()
    if not config:
        logging.error("Problem in creating config file.")
        raise ValueError("Cannot generate config file")
        exit(1)

    generator = Generator(config)
    scheduler = BlockingScheduler(daemon=True)

    minutes = int(config.scheduler_interval_in_min)
    seconds = int(config.scheduler_interval_in_sec)
    start_date = '2022-03-14 09:55:00'
    logging.info("Setting up scheduler")
    scheduler.add_job(generator.handler, 'interval', minutes=minutes,
                      seconds=seconds, start_date=start_date)
    logging.info("Scheduler started")
    scheduler.start()



