from pywebpush import webpush, WebPushException
import sqlite3
import json
from abc import ABC, abstractmethod
import os
import pathlib

from util import Singleton


class Notification(dict):
    def __init__(self, title):
        self["title"] = title
        self["options"] = {}
        self["options"]["vibrate"] = True
        self["options"]["silent"] = False

    def set_body(self, body: str):
        self["options"]["body"] = body

    def add_message(self, message: str):
        self["options"]["data"] = {"message": message}


class BaseNotificationHandler(ABC):
    @abstractmethod
    def push(self, notification: Notification):
        pass


@Singleton
class NotificationHandler(BaseNotificationHandler):
    def __init__(self):
        if "PRODUCTION" in os.environ:
            self.db = "handler/buerro.db"
        else:
            self.db = "handler/test.db"

        self.schema = ("user", "endpoint", "p256dh", "auth")

    def save_subscription(self, subscription: dict):
        # TODO determine user
        user = 123456

        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS subscription
                        (user number not null primary key,
                        endpoint text not null,
                        p256dh text,
                        auth text)"""
        )
        values = (
            user,
            subscription["endpoint"],
            subscription["keys"]["p256dh"],
            subscription["keys"]["auth"],
        )
        c.execute("INSERT OR REPLACE INTO subscription VALUES (?,?,?,?)", values)
        conn.commit()
        conn.close()

    def get_subscription(self):
        # TODO determine user
        user = 123456

        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        try:
            c.execute("SELECT * from subscription")
            row = c.fetchone()
            subscription_info = dict(zip(self.schema, row))
            subscription_info = {
                "endpoint": subscription_info["endpoint"],
                "keys": {
                    "p256dh": subscription_info["p256dh"],
                    "auth": subscription_info["auth"],
                },
            }
        except sqlite3.OperationalError as e:
            subscription_info = None
        finally:
            conn.close()
        return subscription_info

    def push(self, notification: Notification):
        key_file = "sec/vapid_private_key.pem"
        if pathlib.Path(key_file).exists():
            priv_key = key_file
        else:
            # snagged from pywebpush/test
            priv_key = (
                "MHcCAQEEIPeN1iAipHbt8+/KZ2NIF8NeN24jqAmnMLFZEMocY8RboAoGCCqGSM49"
                "AwEHoUQDQgAEEJwJZq/GN8jJbo1GGpyU70hmP2hbWAUpQFKDByKB81yldJ9GTklB"
                "M5xqEwuPM7VuQcyiLDhvovthPIXx+gsQRQ=="
            )

        subscription = self.get_subscription()
        if not subscription:
            raise Exception("No user subscribed to notifications.")
        try:
            print(f"pushing to {subscription['endpoint']}")
            webpush(
                subscription_info=subscription,
                data=json.dumps(notification),
                vapid_private_key=priv_key,
                vapid_claims={"sub": "mailto:buerro@icloud.com"},
            )
        except WebPushException as ex:
            print("Failed to push notification: {}", repr(ex))

            if ex.response and ex.response.json():
                extra = ex.response.json()
                print(
                    "Remote service replied with a {}:{}, {}",
                    extra.code,
                    extra.errno,
                    extra.message,
                )


if __name__ == "__main__":
    os.environ["PRODUCTION"] = "1"
    notification = Notification("Test Notification")
    notification.set_body("You have a new message.")
    notification.add_message(
        """Hey it's me the PDA for your buerro.
        Should I order some Kaesspaetzle?"""
    )
    notification_handler = NotificationHandler.instance()
    notification_handler.push(notification)
