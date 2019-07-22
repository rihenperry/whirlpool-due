# import sys libs
import os, logging

# import third-party libs
from pika import PlainCredentials, ConnectionParameters
from pika import BlockingConnection


def auth_rmq():
    from settings import RMQ
    print('importing rabbitmq settings ok...')

    creds = PlainCredentials(RMQ['username'], RMQ['password'])
    params = ConnectionParameters(host=RMQ['hostname'],
                                  port=RMQ['port'],
                                  virtual_host=RMQ['vhost'],
                                  credentials=creds)

    conn = BlockingConnection(params)
    print('authenticated to rabbitmq as user: {u}, node: {h}, vhost: {v}'.format(u=RMQ['username'],
                                                                                 h=RMQ['hostname'],
                                                                                 v=RMQ['vhost']))
    channel = conn.channel()
    channel.confirm_delivery()
    channel.basic_qos(prefetch_count=1)
    print('publish message confirmation delivery enabled. prefetch count set to {}'.format(1))
    return (conn, channel)

def auth_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from settings import DATABASES

    session = None
    if os.getenv('PY_ENV') == 'development':
        dev_creds = DATABASES['dev']
        print('connecting to dev database {0} '.format(dev_creds['hostname']))

        postgres_conn_str = 'postgresql+psycopg2://{uname}:{pwd}@{host}:{port}/{db}'.format(
            uname=dev_creds['username'],
            pwd=dev_creds['password'],
            host=dev_creds['hostname'],
            port=dev_creds['port'],
            db=dev_creds['dbname'])
        postgres_engine = create_engine(postgres_conn_str)

        # create a configured session class
        Session = sessionmaker(bind=postgres_engine)

        # create a session
        db_conn = postgres_engine.connect()
        session = Session(bind=db_conn)

        print('authentication to {0} database as user: {1} ....ok'.format(dev_creds['hostname'],
                                                                          dev_creds['username']))
        return session
    elif os.getenv('PY_ENV') == 'production':
        print('connection to {1} database'.format(os.getenv('PY_ENV')))
        return session
    else:
        raise LookupError('database environment not defined')
