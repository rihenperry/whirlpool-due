# import sys libs
import os, logging
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers

import threading
import functools

# import third-party libs
from pika import PlainCredentials, ConnectionParameters
from pika import BlockingConnection
from coloredlogging import ColoredFormatter, formatter_message

lock = threading.Lock()


def synchronized(lock):
    """decorator to synchronize instance method"""
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args, **kw):
            with lock:
                return f(*args, **kw)
        return inner_wrapper
    return wrapper


class Singleton(type):
    _instances = {}

    @synchronized(lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class UrlfilterLogging(metaclass=Singleton):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        change_formatter = "[$BOLD%(asctime)s:%(threadName)s-20s$RESET][%(levelname)-1s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
        formatter = logging.Formatter('%(asctime)s:%(threadName)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s')

        CHECK_COLOR_FORMAT = formatter_message(change_formatter, True)
        color_format = ColoredFormatter(CHECK_COLOR_FORMAT)

        # enable file logging
        filepath = os.path.join('logs', 'rotating.log')
        file_handler = RotatingFileHandler(filepath, maxBytes=(1048576*50), backupCount=10)
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(formatter)

        # enable stream logging
        console = logging.StreamHandler()
        console.setFormatter(color_format)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console)

    def getLogger(self):
        return self.logger


log = UrlfilterLogging().getLogger()

def auth_rmq():
    from settings import RMQ
    log.info('importing rabbitmq settings ok...')

    creds = PlainCredentials(RMQ['username'], RMQ['password'])
    params = ConnectionParameters(host=RMQ['hostname'],
                                  port=RMQ['port'],
                                  virtual_host=RMQ['vhost'],
                                  credentials=creds)

    conn = BlockingConnection(params)
    log.info('authenticated to rabbitmq as user: {u}, node: {h}, vhost: {v}'.format(u=RMQ['username'],
                                                                                 h=RMQ['hostname'],
                                                                                 v=RMQ['vhost']))
    channel = conn.channel()
    channel.confirm_delivery()
    channel.basic_qos(prefetch_count=1)
    log.info('publish message confirmation delivery enabled. prefetch count set to {}'.format(1))
    return (conn, channel)

def auth_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from settings import DATABASES

    session = None
    postgres_conn_str = 'postgresql+psycopg2://{uname}:{pwd}@{host}:{port}/{db}'
    auth_stmt = 'authentication to {0} database as user: {1} ....ok'

    if os.getenv('PY_ENV') == 'development':
        dev_creds = DATABASES['dev']
        log.info('connecting to database {0} '.format(dev_creds['hostname']))

        postgres_conn_str = postgres_conn_str.format(
            uname=dev_creds['username'],
            pwd=dev_creds['password'],
            host=dev_creds['hostname'],
            port=dev_creds['port'],
            db=dev_creds['dbname'])

        auth_stmt = auth_stmt.format(dev_creds['hostname'], dev_creds['username'])
    elif os.getenv('PY_ENV') == 'production':
        log.info('connection to database {0}'.format(os.getenv('PY_ENV')))

        postgres_conn_str = postgres_conn_str.format(
            uname=os.getenv('RDS_USER'),
            pwd=os.getenv('RDS_PWD'),
            host=os.getenv('RDS_ENDPOINT'),
            port=os.getenv('RDS_PORT'),
            db=os.getenv('RDS_DB'))

        auth_stmt = auth_stmt.format(os.getenv('RDS_ENDPOINT'), os.getenv('RDS_USER'))
    else:
        raise LookupError('database environment not defined')

    postgres_engine = create_engine(postgres_conn_str)

    # create a configured session class
    Session = sessionmaker(bind=postgres_engine)

    # create a session
    db_conn = postgres_engine.connect()
    session = Session(bind=db_conn)

    log.info(auth_stmt)

    return session

def auth_memcache_db():
    from pymemcache.client.base import Client
    from settings import MEMCACHE

    auth_stmt = 'connecting to {0} memcached instance. host: {1} '
    client = None

    if os.getenv('PY_ENV') == 'development':
        auth_stmt = auth_stmt.format(os.getenv('PY_ENV'), MEMCACHE['hostname'])
        client = Client((MEMCACHE['hostname'], MEMCACHE['port']))
    elif os.getenv('PY_ENV') == 'production':
        auth_stmt = auth_stmt.format(os.getenv('PY_ENV'), os.getenv('MEMCACHE_ENDPOINT'))
        client = Client((os.getenv('MEMCACHE_ENDPOINT'), os.getenv('MEMCACHE_PORT')))
    else:
        raise LookupError('unable to find memcached config')

    log.info(auth_stmt)
    return client
