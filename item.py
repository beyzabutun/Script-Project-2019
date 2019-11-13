# from isbntools.app import *
from isbnlib import meta, is_isbn10, is_isbn13, _exceptions
import sqlite3
import user as _u
from datetime import datetime, timedelta
from database import db


class Item:
    REQUEST_TYPES = {
        'WATCH': 0,
        'BORROW': 1
    }

    STATE = {
        'NOFRIEND': 0,
        'CLOSEFRIEND': 1,
        'FRIEND': 2
    }
    STATE_TYPE = {
        'CLOSED': 0,
        'CLOSEFRIENDS': 1,
        'FRIENDS': 2,
        'EVERYONE': 3,
    }

    # conn = db.DBConnection()

    def __init__(self, owner, item_type=None, title=None, uniqid=None, artist=None, genre=None, year=None):
        # assert self.conn
        # self.db_conn = self.conn.curs
        db_cur = db.get_cursor()
        user_id = db_cur.execute("select id from Users where email like \'{m}\'".format(m=owner.email))
        user_id = user_id.fetchone()[0]
        self.owner = owner
        self.item_type = item_type
        self.genre = genre
        self.rate = 0
        self.location = None
        if uniqid is None:
            self.title = title
            self.uniqid = uniqid
            self.artist = artist
            self.year = year
            db.insert("Items", ('owner', 'type', 'title', 'uniqueid', 'artist', 'genre', 'year'), user_id, item_type, title, uniqid, artist, genre, year)
            self.id = db_cur.execute("select last_insert_rowid()").fetchone()[0]
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
                db.insert("Items", ('owner', 'type', 'title', 'uniqueid', 'artist', 'genre', 'year'), user_id, item_type, self.title, uniqid, self.artist, self.genre,
                                    self.year)
                self.id = db_cur.execute("select last_insert_rowid()").fetchone()[0]

    def borrowed_req(self, user):
        db_cur = db.get_cursor()
        db.insert("BorrowRequests", ('user_id', 'item_id', 'request_date'), user.id, self.id, datetime.now())
        fetched_users = db_cur.execute('select user_id from BorrowRequests order by datetime(request_time) where item_id={item} ;'.format(item=self.id)).fetchall()
        print(fetched_users)
        return fetched_users

    def borrowed_by(self, user, return_date=2):
        db_cur = db.get_cursor()
        taking_date = datetime.now()
        return_date = taking_date + timedelta(weeks=return_date)
        db.insert("Borrows", ('user_id', 'item_id', 'taking_date', 'return_date', 'is_returned'), user.id, self.id, datetime.now(), return_date, 0)
        db_cur.execute('delete from BorrowRequests where user_id={user} and item_id={item} ;'.format(user=user.id, item=self.id ))
        db.connection.commit()

    def returned(self, location=None):
        db_cur = db.get_cursor()
        db_cur.execute("update Borrows set is_returned=1 where is_returned=0 and item_id={id};".format(id=self.id))
        self.location = location
        db.execute("update Items set location=\'{loc}\' where id={id};".format(loc=location, id=self.id))
        # TODO:
        # send notification to users who watches the item to borrow
        # delete watchrequest after notification
        self.conn.connection.commit()

    def comment(self, user, comment_text):
        db.insert("Comments", ('user_id', 'item_id', 'comment', 'date'), user.id, self.id, comment_text, datetime.now())
        # TODO:
        # send notification to users who watches the item to watch

    def list_comments(self):
        db_cur = db.get_cursor()
        fetched_comments = db_cur.execute('select user_id, comment from Comments order by datetime(date) where item_id=\'{item}\''.format(item=self.id)).fetchall()
        print(fetched_comments)
        return fetched_comments

    def rate(self, user, rating):
        db_cur = db.get_cursor()
        db_cur.execute('update Borrows set rate={rate} where item_id={item} and user_id ={user} and is_returned=1 ; '.format(user=user.id, item=self.id))
        db.connection.commit()

    def get_rating(self):
        db_cur = db.get_cursor()
        avg_rating = db_cur.execute('select avg(rate) from Borrows where item_id={item} and rate is not null;').fetchone()[0]
        print(avg_rating)
        return avg_rating

    def locate(self, location):
        db_cur = db.get_cursor()
        db_cur.execute("update Items set location=\'{loc}\' where id={id};".format(loc=location, id=self.id))
        db.connection.commit()

    def setstate(self, state_type, state):
        db_cur = db.get_cursor()
        db_cur.execute("update Items set {state_type}={state} where item_id={item}".format(item=self.id, state_type=state_type, state=self.STATE_TYPE[state]))
        db.connection.commit()

    @classmethod
    def search(cls, user, search_text, genre, year, for_borrow=False):
        db_cur = db.get_cursor()
        words_text = list(search_text.split(" "))
        # in sqlite default like statement is case insensitive already
        state_friend = db_cur.execute('select state from Friends where sender_user={user} or receiver_user={user}').fetchone()[0]
        if year:
            dt = datetime(year=year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            print(dt)
            if for_borrow:
                state_friend = self.db_conn.execute('select state from Friends where (sender_user={user} and receiver_user=) or receiver_user={user}').fetchone()[0]
                f_string = f'select user_id, item_id from Items where {"artist like ? " * len(words_text)} or {"title like ? " * len(words_text)} where datetime(year)>={"?"} and borrow>=;'
            else:
                f_string = f'select user_id, item_id from Items where {"artist like ? "*len(words_text)} or {"title like ? "*len(words_text)} where datetime(year)>={"?"} ;'
        else:
            f_string = f'select user_id, item_id from Items where {"artist like ? " * len(words_text)} or {"title like ? " * len(words_text)} where '
        db_cur.execute('select user_id, item_id from Items where artist in  and ')
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