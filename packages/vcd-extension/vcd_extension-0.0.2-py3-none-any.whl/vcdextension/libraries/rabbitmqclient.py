"""
RabbitMQClient

:date: Mar 6, 2021
:author: Aldo Diaz, Marcelo Sureda

The RabbitMQClient class is used to consume messages from RabbitMQ message
broker using blocking connection with Pika library.
This component is mainly responsible for the interaction with vCloud
Director. It encapsulates RabbitMQ connection in order to freed
framework's user from the nitty-gritty details.
NOTE: This implementation is not thread aware.
"""

from abc import ABC, \
    abstractmethod
from base64 import b64encode, \
    b64decode
from json import dumps, \
    loads
from pika import BlockingConnection, \
    ConnectionParameters, \
    PlainCredentials, \
    BasicProperties
from requests import status_codes
from vcdextension.libraries.logger import Logger
from vcdextension.persistence.persistence import Persistence
from vcdextension.libraries.vcloudsecurity import VCloudSecurity


class RabbitMQClient(ABC):
    """
    Consumer for RabbitMQ using Pika
    RabbitMQClient consumes messages from RabbitMQ using blocking connection
    with Pika library.

    :attribute BlockingConnection _connection: RabbitMQ connection object
    :attribute channel.Channel _sub_channel: subscriber channel
    :attribute channel.Channel _pub_channel: publisher channel
    """

    _connection = None
    _sub_channel = None
    _pub_channel = None
    _log = Logger()
    _config = Persistence().get_config()['rabbit']

    def __init__(self):
        """
        Constructor to initialize connection to RabbitMQ.
        The constructor sets up connection, creates subscriber channel, declares
        a queue, an exchange, a publisher channel, and binds to subscriber queue.
        """
        # Initialize and make some noise about it
        self._log.info(f"Initializing {self.__class__.__qualname__}")

        try:
            # Connect and authenticate with RabbitMQ
            self._connection = BlockingConnection(ConnectionParameters(
                host=self._config['host'],
                port=self._config['port'],
                credentials=PlainCredentials(self._config['user'],
                                             self._config['password'])))
            self._log.info(f"Successfully authenticated on RabbitMQ Server {self._config['host']}")

            # Create a channel, declare a queue and subscribe to the incoming messages.
            self._sub_channel = self._connection.channel()
            self._sub_channel.exchange_declare(exchange=self._config['exchange'],
                                               exchange_type='direct',
                                               durable=True)
            self._sub_channel.queue_declare(queue=self._config['routingkey'])
            self._sub_channel.queue_bind(exchange=self._config['exchange'],
                                         queue=self._config['routingkey'])

            # Create a channel for publishing messages back to the client.
            self._pub_channel = self._connection.channel()

            # Bind to the the queue we will be listening on with a callback function.
            self._sub_channel.basic_consume(queue=self._config['routingkey'],
                                            on_message_callback=self.__on_message,
                                            auto_ack=True)
            # TODO Analyze BlockingConnection.add_timeout

            self._log.info(f"Bind made to exchange {self._config['exchange']} "
                           f"and queue {self._config['routingkey']}")

        except Exception as e:
            self._log.error(f"<<{type(e).__qualname__}>> {e}")
            raise e

    def start_consuming(self):
        """
        Begin monitoring for incoming messages
        Starts to continuously monitor the queue for messages. After calling
        this method the thread will remain blocked waiting for a message.
        """
        if self._sub_channel is None:
            self._log.error(f"Bind not made to exchange {self._config['exchange']} and "
                            f"queue {self._config['routingkey']} - Message consuming not started")
        else:
            self._log.info(f"Start consuming from queue {self._config['routingkey']}")
            # TODO Handle exception conditions
            # pika.exceptions.AMQPHeartbeatTimeout:
            #   No activity or too many missed heartbeats in the last 580 seconds
            self._sub_channel.start_consuming()

    def __on_message(self, ch, method, properties, body):
        """
        Handle messages received on the RabbitMQ Exchange
        Calls the method process_message_received to process the message.

        :param channel.Channel ch: channel object
        :param spec.Basic.Deliver method: basic deliver method
        :param bytes body: message body
        :param spec.BasicProperties properties: message properties
        """
        try:
            body = loads(body)
            # Log request message id
            self._log.info(f"Ctx={body[0]['id']} received with "
                           f"correlation id={properties.correlation_id}")

            # Save message and security context
            vcd_security = VCloudSecurity()
            vcd_security.add_context(body[0]['id'], body)

            # Body message must be decoded from its BASE64 form
            request_body_ascii = str(b64decode(body[0]['body']))[2:-1]

            # If it's in JSON format, must be deserialized
            if 'Content-Type' in body[0]['headers']:
                if body[0]['headers']['Content-Type'] == "application/json":
                    request_body_ascii = request_body_ascii.replace('\\n', '')
                    body[0]['body'] = loads(request_body_ascii)
            self._log.debug(f"Request body received: {body[0]['body']}")
            resp_code, resp_body = self.process_request(body[0])
        except Exception as e:
            self._log.error(f"<<{type(e).__qualname__}>> {e}")
            resp_code, resp_body = status_codes.codes.server_error, {'response': str(e)}
        self._log.debug(f"Response sent: Status Code: {resp_code} - Message body: {resp_body}")
        self.__send_message_response(ch, method, properties, body, resp_code, resp_body)

    def __send_message_response(self, ch, method, properties, body, resp_code=None, resp_body=None):
        """
        This method formats and sends the response back to RabbitMQ.

        :param channel.Channel ch: channel object
        :param spec.Basic.Deliver method: basic deliver method
        :param spec.BasicProperties properties: message properties
        :param list(dict) body: message body
        :param int resp_code: response status code
        :param dict resp_body: response body
        """
        if resp_body is None or resp_code is None:
            resp_code = status_codes.codes.server_error
            resp_body = {'response': 'response not set by server'}
        try:
            # Remove security context
            vcd_security = VCloudSecurity()
            vcd_security.del_context(body[0]['id'])

            # Since Python 3.5 bytes-like object is required for b64encode
            # BASE64 encoding must be handled accordingly in order to call json.dumps
            resp_body_str = dumps(resp_body)
            resp_body_b64 = str(b64encode(resp_body_str.encode('UTF-8')))[2:-1]

            # Build the response message to return
            resp_msg = {'id': body[0]['id'],
                        'headers': {'Content-Type': body[0]['headers']['Accept'],
                                    'Content-Length': len(resp_body_str)},
                        'statusCode': resp_code,
                        'body': resp_body_b64,
                        'request': False}

            # vCD sets unique correlation_id in every message sent to extension and the
            # extension must set the same value in the corresponding response.
            resp_properties = BasicProperties(correlation_id=properties.correlation_id)

            # We send our response to the Exchange and queue that were specified in
            # the received properties.
            self._pub_channel.basic_publish(properties.headers['replyToExchange'],
                                            properties.reply_to,
                                            bytes(dumps(resp_msg), 'UTF-8'),
                                            resp_properties)
            self._log.info(f"Ctx={body[0]['id']}: Response sent with correlation id={properties.correlation_id}")

        except Exception as e:
            self._log.error(f"Ctx={body[0]['id']}: <<{type(e).__qualname__}>> {e}")

    @abstractmethod
    def process_request(self, body):
        """
        Process the request and executes the backend operations.
        This method must be overridden via class inheritance.

        :param list body: message body
        :return: int resp_code: status code to respond to frontend,
                 dict resp_body: body with response or error detail
        """

    def close_connection(self):
        """
        Close active connection to RabbitMQ server
        """
        try:
            self._connection.close()
            self._log.info(f"RabbitMQ connection successfully closed")
        except Exception as e:
            self._log.error(f"<<{type(e).__qualname__}>> {e}")
