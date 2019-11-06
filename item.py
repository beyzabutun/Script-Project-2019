
class Item():

    def __init__(self, owner, item_type, title, uniqid, artist, genre, year):
        self.owner = owner
        self.item_type = item_type
        self.title = title
        self.uniqid = uniqid
        self.artist = artist
        self.genre = genre
        self.year = year

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

