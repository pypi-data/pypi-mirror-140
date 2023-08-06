from kombu import Connection, Exchange, Producer

from kombu_producer.utils import Singleton


class KombuProducer(metaclass=Singleton):

    def __init__(self, exchange_name, exchange_type, routing_key, broker_url):
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        self.__connect(broker_url)

    def __connect(self, broker_url):
        self.__conn = Connection(broker_url)
        self.__channel = self.__conn.channel()
        self.__exchange = Exchange(self.exchange_name, type=self.exchange_type)
        self._producer = Producer(
            exchange=self.__exchange,
            channel=self.__channel,
            routing_key=self.routing_key,
        )

    def publish_payload(self, payload):
        publish = self.__conn.ensure(self._producer, self._producer.publish, max_retries=3)
        publish(payload)
