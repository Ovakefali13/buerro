from pywebpush import webpush, WebPushException
import sqlite3


conn = sqlite3.connect('buerro.db')
c = conn.cursor()
c.execute('SELECT * from subscription')
row = c.fetchone()
schema = ('endpoint', 'p256dh', 'auth')
subscription_info = dict(zip(schema, row))
subscription_info = {
    'endpoint': subscription_info['endpoint'],
    'keys': {
        'p256dh': subscription_info['p256dh'],
        'auth': subscription_info['auth']
    }
}
conn.close()

try:
    webpush(
        subscription_info=subscription_info,
        data="Mary had a little lamb, with a nice mint jelly",
        vapid_private_key="sec/vapid_private_key.pem",
        vapid_claims={
                "sub": "mailto:buerro@icloud.com"
            }
    )
except WebPushException as ex:
    print("I'm sorry, Dave, but I can't do that: {}", repr(ex))
    # Mozilla returns additional information in the body of the response.
    if ex.response and ex.response.json():
        extra = ex.response.json()
        print("Remote service replied with a {}:{}, {}",
              extra.code,
              extra.errno,
              extra.message
              )
