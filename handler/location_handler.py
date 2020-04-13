import sqlite3
import os

from services import PrefService
from util import Singleton


@Singleton
class LocationHandler:
    def __init__(self):
        if "PRODUCTION" in os.environ:
            self.db = "handler/buerro.db"
        else:
            self.db = "handler/test.db"
        self.schema = ("user_id", "lat", "lon")

        self.pref_service = PrefService()  # user id)

    def set_db(self, db):
        self.db = db

    def set(self, lat, lon):
        # TODO user id
        user_id = 12345

        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS last_location
                        (user_id num not null primary key,
                        lat num not null,
                        lon num not null)"""
        )

        values = (user_id, lat, lon)
        c.execute("INSERT OR REPLACE INTO last_location VALUES (?,?,?)", values)
        conn.commit()
        conn.close()

    def get(self):
        # TODO user id
        user_id = 12345

        try:
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            c.execute("SELECT * from last_location WHERE user_id = ?", (user_id,))
            user_id, lat, lon = c.fetchone()
            return lat, lon
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                try:
                    coords = self.pref_service.get_specific_pref("home_coords")
                    if len(coords) != 2:
                        raise Exception("home_coords preference is not a 2-tuple")
                    return coords[0], coords[1]
                except:
                    raise Exception(
                        ("Neither location set nor home address" " specified")
                    )
            else:
                raise e

        finally:
            conn.close()

        return lat, lon
