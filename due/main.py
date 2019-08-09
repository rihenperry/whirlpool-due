# sys libs
import sys, traceback

# dependency libs
import pika
import sqlalchemy

# user libs
import utils
from consumer import consume_from_urlfilter_queue

log = utils.UrlfilterLogging().getLogger()

def main():
    # authenticate to RMQ, POSTGRES, and listen for messages on a direct queue

    try:
        due_session = utils.auth_db()
        conn, channel = utils.auth_rmq()
        consume_from_urlfilter_queue(channel, due_session)
        try:
            channel.start_consuming()
        except KeyboardInterrupt as keyevent:
            log.error('caught key interrupt {}, closing rmq connection'.format(keyevent))
            channel.stop_consuming()
            conn.close()
    except LookupError as lookup_err:
        log.error('LookupError {}, stopping...'.format(lookup_err))
        traceback.print_exc(file=sys.stdout)
        sys.exit()

    except pika.exceptions.ConnectionClosedByBroker as broker_stopped:
        log.error('borker closed connection{}, '.format(broker_stopped))
        conn.close()
    except pika.exceptions.AMQPChannelError as amqperror:
        log.error("Caught a channel error: {}, stopping...".format(amqperror))
    except pika.exceptions.AMQPConnectionError as allother:
        log.error("Caught other misc AMQP error : {}, stopping...".format(allother))
    except sqlalchemy.exc.SQLAlchemyError as sqlerr:
        log.error("Caught SQLAlchemy error : {}, stopping...".format(sqlerr))



if __name__ == '__main__':
    log.info("executing %s" % __file__)
    main()
