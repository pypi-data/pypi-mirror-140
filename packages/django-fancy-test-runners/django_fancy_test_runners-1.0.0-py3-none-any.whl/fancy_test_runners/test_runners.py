import logging
import os
import socket
import stat

import mock

from django.db import connection
from django.test.runner import DiscoverRunner


logger = logging.getLogger(__name__)


class CeleryDisablingTestRunner(DiscoverRunner):
    def run_tests(self, *args, **kwargs):
        def mocked_send_task(*send_task_args, **sent_task_kwargs):
            raise Exception('Don\'t use Celery in tests! See http://docs.celeryproject.org/en/latest/userguide/testing.html for more details.')
        with mock.patch('celery.Celery.send_task', mocked_send_task):
            return super().run_tests(*args, **kwargs)


class InternetDisablingTestRunner(DiscoverRunner):

    TEST_IP_WHITELIST = [
        '0.0.0.0',
        '127.0.0.1',
        'localhost',
    ]

    def run_tests(self, *args, **kwargs):
        """Block Internet access during tests"""
        old_connect = socket.socket.connect

        def connect(socket_self, address):
            # file socket connection
            if isinstance(address, str) and stat.S_ISSOCK(os.stat(address).st_mode):
                return old_connect(socket_self, address)
            # IP socket
            host, port = address
            if host in self.TEST_IP_WHITELIST:
                return old_connect(socket_self, address)
            logger.warning('Blocking a socket connection to %s:%d', host, port)
            raise Exception('I told you not to use the Internet!')

        with mock.patch('socket.socket.connect', connect):
            return super().run_tests(*args, **kwargs)


class SqlDumpLoadingTestRunner(DiscoverRunner):

    def __init__(self, db_template_path=None, **kwargs):
        super().__init__(**kwargs)
        self.db_template_path = db_template_path or os.getenv('DB_TEMPLATE_PATH')

    def setup_databases(self, **kwargs):
        if self.db_template_path:
            connection.creation.test_db_template_path = self.db_template_path
        return super().setup_databases(**kwargs)
