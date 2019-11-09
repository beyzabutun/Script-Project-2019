# from isbntools.app import *
from isbnlib import meta, is_isbn10, is_isbn13, _exceptions


class Item:

    db_conn = None

    def __init__(self, owner, item_type=None, title=None, uniqid=None, artist=None, genre=None, year=None):
        self.db_conn = self.db_conn.cursor()

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
            # self.db_conn.execute('''insert into Items values (owner, type, title,
            # uniqueid, artist, genre, year, location, rate)''', )

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

    def borrowed_req(self, user):

        pass

    def borrowed_by(self, user, return_date=2):
        pass

    def returned(self, location=None):
        pass

    def comment(self, user, comment_text):
        pass

    def list_comments(self):
        pass

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

