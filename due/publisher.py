# dep libs
import pika

from utils import UrlfilterLogging


log = UrlfilterLogging().getLogger()

# urlfilter publish
def publish_to_urlfrontier_queue(channel, msg):
    pub_confirm = False
    log.info('invoked {0}'.format(publish_to_urlfrontier_queue.__name__))
    try:
        channel.basic_publish(exchange='urlfilter.ex.due',
                              routing_key='due_p.to.urlfrontier_c',
                              body=msg,
                              properties=pika.BasicProperties(content_type='application/json',
                                                              delivery_mode=2),
                              mandatory=True)
        pub_confirm = True
    except pika.exceptions.UnroutableError as push_fail_err:
        log.error('Message publish could not be confirmed {0}'.format(push_fail_err))

    return pub_confirm
