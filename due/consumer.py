# sys imports
import pickle
from functools import partial

# local imports
import publisher

# whirlpool-urlfilter consume
def consume_from_urlfilter_queue(channel, session):
    print('invoked {0}'.format(consume_from_urlfilter_queue.__name__))
    on_msg_callback_with_session = partial(on_msg_callback, db_session=session)
    channel.basic_consume('due.q', on_msg_callback_with_session)
    print('consumer listening for messages on due.q')

def on_msg_callback(channel, method_frame, header_frame, body, db_session):
     print('delivery tag {}'.format(method_frame.delivery_tag))
     print('header_frame {}'.format(header_frame))
     print('msg body {}'.format(body))

     # do some processing with dbsession
     #
     #
     try:
         # db_session.query(FooBar).update({"x": 5})
         db_session.commit()
         print('work processed. session committed')
     except:
         print('db session failed')
         db_session.rollback()
         raise

     # finally send message by call publisher
     msg = {
         'urls': ['http://a1.com', 'http://a2.com', 'http://a3.com']
     }

     bmsg = pickle.dumps(msg)
     pub_confirm = publisher.publish_to_urlfrontier_queue(channel, bmsg)
     if pub_confirm:
         channel.basic_ack(delivery_tag=method_frame.delivery_tag)
         print('message from urlfrontier.q acknowledged')
     else:
         channel.basic_nack(delivery_tag=method_frame.delivery_tag)
         print('message from urlfrontier.q acknowledgement failed')
