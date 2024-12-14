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
    PERCEPTION = '/bang/perception'
    PREDICTION = '/bang/prediction'
    PLANNING = '/bang/planning'

    @staticmethod
    def publish(topic, data):
        if isinstance(data, dict):
            data = json.dumps(data)
        r.publish(topic, data)

    @staticmethod
    def subscribe(topics):
        logging.info(F'Subscribed to topic {topics}.')
        single_mode = isinstance(topics, str)
        p = r.pubsub()
        if single_mode:
            p.subscribe(topics)
        else:
            for topic in topics:
                p.subscribe(topic)

        for message in p.listen():
            if message['type'] == 'message':
                yield message['data'] if single_mode else (message['channel'].decode(), message['data'])
