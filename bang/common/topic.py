import json

from absl import logging
import redis


REDIS_HOST = 'localhost'
REDIS_PORT = 6379

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


class Topic(object):
    CAMERA = '/bang/camera'
    CHASSIS = '/bang/chassis'
    CONTROL = '/bang/control'

    @staticmethod
    def publish(topic, data):
        if isinstance(data, dict):
            data = json.dumps(data)
        r.publish(topic, data)

    @staticmethod
    def subscribe(topics):
        logging.info(F'Subscribed to topic {topics}.')
        p = r.pubsub()
        if isinstance(topics, str):
            p.subscribe(topics)
        else:
            for topic in topics:
                p.subscribe(topic)

        for message in p.listen():
            if message['type'] == 'message':
                yield message['channel'].decode(), message['data']
