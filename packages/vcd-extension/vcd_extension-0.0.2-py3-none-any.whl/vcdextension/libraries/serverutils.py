"""
ServerUtils

:date: Sep 15, 2021
:author: Aldo Diaz, Marcelo Sureda

The Server Utils class exposes functionality that can be used by the server.
"""
import sys

from vcdextension import VERSION
from vcdextension.libraries.logger import Logger
from vcdextension.libraries.taskscheduler import TaskScheduler
from vcdextension.libraries.vcloudsecurity import VCloudSecurity


class ServerUtils:
    """
    Class which exposes server's helper functions
    """
    _log = Logger()
    _message_broker_client = None

    def __init__(self, service_cls):
        """
        Init server and catch interruption signal

        :param service_cls: User Class which overrides Service RabbitMQ
        """
        ServerUtils._log.info(f"vcd Extension Backend server is starting. "
                              f"Server version {'.'.join([str(x) for x in VERSION])}")
        self._message_broker_client = service_cls()

    def init_server(self):
        """
        Start task scheduler and start to continuously
        monitor the queue for messages.
        """
        TaskScheduler()
        self._message_broker_client.start_consuming()

    def cleanup(self):
        """
        Handle a Keyboard Interrupt to leave gracefully
        closing all external connections
        """
        # Hide the ^C
        sys.stdout.write('\b\b\r')
        ServerUtils._log.info(f"Signal Keyboard Interrupt received - Preparing to exit")
        ServerUtils._log.info("Closing RabbitMQ connection")
        self._message_broker_client.close_connection()
        ServerUtils._log.info("Shutting down scheduler")
        TaskScheduler().stop_scheduler()
        ServerUtils._log.info("Logging out from vCloud Director server")
        VCloudSecurity().logout()
        ServerUtils._log.info("Shutting down vcd Extension Backend server")
        sys.exit(0)
