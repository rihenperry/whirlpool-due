# sys imports
import json
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
     print('msg body {}'.format(json.loads(body)))

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
         "1": [{"type": "c", "url": "http://ex1.com/hola"}],
         "2": [{"url": "http://ex4.com/new", "type": "nc"}, {"type": "c", "url": "http://ex10.com"}],
         "3": [{"url": "http://ex3.com/xyz/def", "type": "nc"}]
     };

     bmsg = json.dumps(msg).encode('utf-8')
     pub_confirm = publisher.publish_to_urlfrontier_queue(channel, bmsg)
     if pub_confirm:
         channel.basic_ack(delivery_tag=method_frame.delivery_tag)
         print('message from urlfrontier.q acknowledged')
     else:
         channel.basic_nack(delivery_tag=method_frame.delivery_tag)
         print('message from urlfrontier.q acknowledgement failed')
