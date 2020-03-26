import unittest
from unittest.mock import patch
import random
import string
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from threading import Thread
import time
import requests
from copy import copy
import os
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import queue


from .. import NotificationHandler, Notification
from .. import UsecaseStore
from usecase import Usecase

class MockUsecase(Usecase):
    def __init__(self):
        self.count = 0
    def advance(self, message):
        if self.is_finished(): self.reset()
        self.count += 1
        if self.count == 1:
            return "test1"
        if self.count == 2:
            return "test2"
        raise Exception("advanced finished usecase")

    def is_finished(self):
        return self.count == 2

    def reset(self):
        self.count = 0

    def set_default_services(self):
        pass

class TestNotificationHandler(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.notification_handler = NotificationHandler.instance()
        UsecaseStore.instance().purge()

    def get_random_subscription(self):
        def _get_random_p256dh():
            recv_key = ec.generate_private_key(ec.SECP256R1, default_backend())
            return base64.urlsafe_b64encode(recv_key.public_key().public_bytes(
                        encoding=serialization.Encoding.X962,
                        format=serialization.PublicFormat.UncompressedPoint
                    )).strip(b'=')

        return {
                'endpoint': "https://example.com/",
                'keys': {
                    'p256dh': _get_random_p256dh(),
                    'auth': base64.urlsafe_b64encode(os.urandom(16)).strip(b'='),
                    }
               }

    def test_set_and_get_subscription_info(self):
        mock_subscription = self.get_random_subscription()
        self.notification_handler.save_subscription(mock_subscription)
        ret = self.notification_handler.get_subscription()

        self.assertEqual(ret, mock_subscription)

