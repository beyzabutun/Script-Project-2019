# from isbntools.app import *
from isbnlib import meta, is_isbn10, is_isbn13, _exceptions
import sqlite3
import user as _u
from datetime import datetime, timedelta
import database as db


class Item:
    REQUEST_TYPES = (
        (0, "WATCH"),
        (1, "BORROW")
    )
    STATE_TYPE = (
        (0, "CLOSED"),
        (1, "FRIENDS"),
        (2, "CLOSEFRIENDS"),
        (3, "EVERYONE"),
    )

    conn = db.DBConnection()

    def __init__(self, owner, item_type=None, title=None, uniqid=None, artist=None, genre=None, year=None):
        assert self.conn
        self.db_conn = self.conn.curs
        user_id = self.db_conn.execute("select id from Users where email like \'{m}\'".format(m=owner.email))
        user_id = user_id.fetchone()[0]
        self.owner = owner
        if uniqid is None:
            self.item_type = item_type
            self.title = title
            self.uniqid = uniqid
            self.artist = artist
            self.genre = genre
            self.year = year
            self.rate = 0
            self.location = None
            self.conn.insert("Items", None, user_id, item_type, title, uniqid, artist, genre, year, None, 0)
            self.id = self.db_conn.execute("select last_insert_rowid()").fetchone()[0]

        else:
            metadata = None
            try:
                metadata = meta(isbn=uniqid)
            except Exception as ex:
                print(ex)
            if metadata is not None:
                self.title = metadata['title']
                self.year = metadata['Year']
                self.artist = metadata['Authors'][0]
                self.item_type = item_type
                self.genre = genre
                self.rate = 0
                self.location = None
                self.db_conn.insert("Items", None, user_id, item_type, self.title, uniqid, self.artist, self.genre,
                                    self.year, None, 0)

    def borrowed_req(self, user):
        self.conn.insert("Requests", None, user.id, self.id, datetime.now(), self.REQUEST_TYPES[1][0])

    def borrowed_by(self, user, return_date=2):
        taking_date = datetime.now()
        return_date = taking_date + timedelta(weeks=return_date)
        self.conn.insert("Borrows", None, user.id, self.id, datetime.now(), return_date, 0)

    def returned(self, location=None):
        self.db_conn.execute("update Borrows set is_returned=1 where is_returned=0 and item_id={id};".format(id=self.id))
        self.location = location
        self.db_conn.execute("update Items set location=\'{loc}\' where id={id};".format(loc=location, id=self.id))
        self.conn.connection.commit()

    def comment(self, user, comment_text):
        self.conn.insert("Comments", None, user.id, self.id, comment_text, datetime.now())

    def list_comments(self):


    def rate(self, user, rating):
        self.rate += 1
        pass

    def get_rating(self):

        pass

    def locate(self, location):
        pass

    def setstate(self, state_type, state):
        pass

    def search(self, user, search_text, genre, year, for_borrow=False):
        pass

    def watch(self, user, watch_method):
        pass

    def view(self, user):
        pass

    def detail(self, user):
        pass

    def announce(self, owner_type, msg):
        pass

    def delete(self):
        pass


user = _u.User("beste", "burhan", "beste.com", "password")
user2 = _u.User("beste", "burhan", "bestee.com", "password")
user3 = _u.User("beste", "burhan", "besteee.com", "password")
it = Item(user, "type", "title", None, "artist", "genre", 1996)
it2 = Item(user, "type", "title", None, "artist", "genre", 1996)
it3 = Item(user, "type", "title", None, "artist", "genre", 1996)
it4 = Item(user, "type", "title", None, "artist", "genre", 1996)
it3.borrowed_by(user)
it3.returned("location")