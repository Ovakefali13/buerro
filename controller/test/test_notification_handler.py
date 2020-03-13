import unittest
import random
import string

from .. import NotificationHandler

class TestNotificationHandler(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.notification_handler = NotificationHandler()
        self.notification_handler.set_db('controller/test/test.db')

    def test_set_and_get_subscription_info(self):
        subscription_info = {
            'endpoint': 'test@endpoint.com',
            'keys': {
                'p256dh': ''.join(random.choices(string.ascii_uppercase +
                    string.digits,k=10)),
                'auth': ''.join(random.choices(string.ascii_uppercase +
                    string.digits,k=10))
            }
        }
        self.notification_handler.save_subscription(subscription_info)
        ret = self.notification_handler.get_subscription()

        self.assertEqual(ret, subscription_info)
