from pywebpush import webpush, WebPushException
import sqlite3
import json


class Notification(dict):
    def __init__(self, title):
        self['title'] = title
        self['options'] = {}
        self['options']['vibrate'] = True
        self['options']['silent'] = False

    def set_body(self, body):
        self['options']['body'] = body

class NotificationHandler:

    def __init__(self):
        self.db = 'buerro.db'
        self.schema = ('endpoint', 'p256dh', 'auth')

    def set_db(self, db:str):
        self.db = db

    def save_subscription(self, subscription:dict):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscription
                        (endpoint text not null primary key,
                        p256dh text,
                        auth text)''')
        values = (subscription['endpoint'], subscription['keys']['p256dh'],
            subscription['keys']['auth'])
        c.execute('INSERT OR REPLACE INTO subscription VALUES (?,?,?)', values)
        conn.commit()
        conn.close()

    def get_subscription(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('SELECT * from subscription')
        row = c.fetchone()
        subscription_info = dict(zip(self.schema, row))
        subscription_info = {
            'endpoint': subscription_info['endpoint'],
            'keys': {
                'p256dh': subscription_info['p256dh'],
                'auth': subscription_info['auth']
            }
        }
        conn.close()
        return subscription_info

    def push(self, notification:Notification):
        try:
            webpush(
                subscription_info=self.get_subscription(),
                data=json.dumps(notification),
                vapid_private_key="sec/vapid_private_key.pem",
                vapid_claims={
                        "sub": "mailto:buerro@icloud.com"
                    }
            )
        except WebPushException as ex:
            print("Failed to push notification: {}", repr(ex))

            if ex.response and ex.response.json():
                extra = ex.response.json()
                print("Remote service replied with a {}:{}, {}",
                      extra.code,
                      extra.errno,
                      extra.message
                      )

if __name__ == "__main__":
    notification = Notification('Test Notification')
    notification.set_body('Did you know? buerro is super cool.')
    notification_handler = NotificationHandler()
    notification_handler.push(notification)
