import sqlite3
from services.singleton import Singleton

@Singleton
class LocationHandler:

    def __init__(self):
        self.db = 'buerro.db'
        self.schema = ('user_id', 'lat', 'lon')

    def set_db(self, db):
        self.db = db

    def set(self, lat, lon):
        # TODO user id
        user_id = 12345

        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS last_location
                        (user_id num not null primary key,
                        lat num not null,
                        lon num not null)''')

        values = (user_id, lat, lon)
        c.execute('INSERT OR REPLACE INTO last_location VALUES (?,?,?)', values)
        conn.commit()
        conn.close()

    def get(self):
        # TODO user id
        user_id = 12345

        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('SELECT * from last_location WHERE user_id = ?', (user_id,))
        user_id, lat, lon = c.fetchone()
        conn.close()
        return lat, lon

