# sys libs
import sys

# dependency libs
import pika
import sqlalchemy

# user libs
import utils
from consumer import consume_from_urlfilter_queue

def main():
    # authenticate to RMQ, POSTGRES, and listen for messages on a direct queue

    try:
        due_session = utils.auth_db()
        conn, channel = utils.auth_rmq()
        consume_from_urlfilter_queue(channel, due_session)
        try:
            channel.start_consuming()
        except KeyboardInterrupt as keyevent:
            print('caught key interrupt {}, closing rmq connection'.format(keyevent))
            channel.stop_consuming()
            conn.close()
    except LookupError as lookup_err:
        print('LookupError {}, stopping...'.format(lookup_err))
        sys.exit()

    except pika.exceptions.ConnectionClosedByBroker as broker_stopped:
        print('borker closed connection{}, '.format(broker_stopped))
        conn.close()
    except pika.exceptions.AMQPChannelError as amqperror:
        print("Caught a channel error: {}, stopping...".format(amqperror))
    except pika.exceptions.AMQPConnectionError as allother:
        print("Caught other misc AMQP error : {}, stopping...".format(allother))
    except sqlalchemy.exc.SQLAlchemyError as sqlerr:
        print("Caught SQLAlchemy error : {}, stopping...".format(sqlerr))



if __name__ == '__main__':
    print("executing %s" % __file__)
    main()
