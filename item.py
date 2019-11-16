from isbnlib import meta
from datetime import datetime, timedelta
from database import db


class Item:
    WATCH_REQUEST_TYPES = {
        "COMMENT": 0,
        "BORROW": 1,  # watch for status change
        "USER": 2
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

    def __init__(self, owner, item_type=None, title=None, uniqid=None, artist=None, genre=None, year=None):
        is_verified = True
        try:
            is_verified = db.connection.cursor().execute('select is_verified from Users where id=?', (owner.id,)).fetchone()[0]
        except:
            print("There is no such user.")
        if not is_verified:
            print("Owner is not verified, item can't be created!")
            return
        else:

            self.cur = db.get_cursor()
            user_id = self.cur.execute("select id from Users where email like \'{m}\'".format(m=owner.email))
            user_id = user_id.fetchone()[0]
            self.owner = owner
            self.item_type = item_type
            self.genre = genre
            self.location = None
            self.view = 2
            self.borrow = 2
            self.detail = 2
            self.comment = 2
            self.search = 2
            self.uniqid = uniqid
            if uniqid is None:
                self.title = title
                self.uniqid = uniqid
                self.artist = artist
                self.year = year
                db.insert("Items", ('owner', 'type', 'title', 'uniqueid', 'artist', 'genre', 'year', 'view',
                                    'detail', 'search', 'borrow', 'comment'), user_id, item_type, title,
                          uniqid, artist, genre, year, 2, 2, 2, 2, 2)
                self.id = self.cur.execute("select last_insert_rowid()").fetchone()[0]
                print(self.id, self, ", item is created.")
            else:
                metadata = None
                try:
                    metadata = meta(isbn=uniqid)
                except Exception as ex:
                    print(ex)
                if metadata is not None:
                    self.title = metadata['Title']
                    self.year = metadata['Year']
                    self.artist = metadata['Authors'][0]
                    db.insert("Items", ('owner', 'type', 'title', 'uniqueid', 'artist', 'genre', 'year', 'view',
                                    'detail', 'search', 'borrow', 'comment'), user_id,
                              item_type, self.title, uniqid, self.artist, self.genre, self.year, 2, 2, 2, 2, 2)
                    self.id = self.cur.execute("select last_insert_rowid()").fetchone()[0]
                    print(self.id, self, " item is created with isbn number : ", self.uniqid)

            # if there is a user who watches owner, send notification followed users
            try:
                users_watching = self.cur.execute(
                    "select user_id from WatchRequests where followed_id={owner} and watch_method={wmethod}".format(owner=owner, wmethod=self.WATCH_REQUEST_TYPES["USER"])).fetchall()
            except:
                users_watching = []
            for user in users_watching:
                self.insert("Notifications", ("sender", "receiver", "item_id", "notification_text", "notification_date"),
                            owner.id, user.id, self.id,
                            "{owner} add new \'{item}\' item.".format(owner=owner, item=self),
                            datetime.now())
                print("Receiver :  ", user, " Notification : ", "{owner} add new \'{item}\' item.".format(owner=owner, item=self))

    def borrowed_req(self, user):
        already_requested = None
        try:
            already_requested = self.cur.execute("select user_id from BorrowRequests where item_id={item} and user_id={user}".format(item=self.id, user=user.id)).fetchone()[0]
        except:
            db.insert("BorrowRequests", ('user_id', 'item_id', 'request_date'), user.id, self.id, datetime.now())
        if already_requested is not None: # true
            print("{user} already requested for this item.".format(user=user))
        fetched_users = self.cur.execute(
            'select user_id from BorrowRequests where item_id={item} order by datetime(request_date)  ;'
                .format(item=self.id)).fetchall()
        result = []
        for user in fetched_users:
            result.append(user[0])
        return result

    def borrowed_by(self, user, return_date=2):
        taking_date = datetime.now()
        return_date = taking_date + timedelta(weeks=return_date)
        alread_borrowed = None
        try:
            alread_borrowed = self.cur.execute(f"select id from Borrows where is_returned=0 and item_id={'?'}", [self.id]).fetchone()[0]
        except:
            db.insert("Borrows", ('user_id', 'item_id', 'taking_date', 'return_date', 'is_returned'), user.id,
                      self.id, datetime.now(), return_date, 0)
            self.cur.execute('delete from BorrowRequests where user_id={user} and item_id={item} ;'
                             .format(user=user.id, item=self.id ))
            db.connection.commit()
        if alread_borrowed is not None:
            print("This item already borrowed.")

    def returned(self, location=None):
        self.cur.execute("update Borrows set is_returned=1 where is_returned=0 and item_id={id};".format(id=self.id))
        self.location = location
        self.cur.execute("update Items set location=\'{loc}\' where id={id};".format(loc=location, id=self.id))
        # TODO:
        # send notification to users who watches the item to borrow
        # delete watchrequest after notification
        db.connection.commit()
        try:
            users_watching = self.cur.execute(
                "select user_id from WatchRequests where item_id={item} watch_method={wmethod}"
                    .format(item=self.id, wmethod=self.WATCH_REQUEST_TYPES["BORROW"])).fetchall()
            self.cur.execute(
                "delete from WatchRequests where item_id={item} watch_method={wmethod}"
                    .format(item=self.id, wmethod=self.WATCH_REQUEST_TYPES["BORROW"]))
            db.connection.commit()
        except:
            users_watching = []
        for user in users_watching:
            self.insert("Notifications",
                        ("sender", "receiver", "item_id", "notification_text", "notification_date"),
                        self.owner.id, user.id, self.id,
                        " \'{item}\' item is returned.".format(item=self),
                        datetime.now())
            print("Receiver :  ", user, " Notification : ", " \'{item}\' item is returned.".format(item=self))

    def make_comment(self, user, comment_text):
        try:
            friend_state = self.cur.execute(
                "select state from Friends where (sender_user = {self_id} and receiver_user = {user_id}) or (sender_user = {user_id} and receiver_user = {self_id})"
                    .format(self_id=self.owner, user_id=user.id)).fetchone()[0]
        except:
            friend_state = 0
        comment = self.cur.execute(
                "select comment from Items where id={item}"
                .format(item=self.id)).fetchone()[0]

        if (comment >= friend_state and friend_state is not 0) or (comment is 3):
            db.insert("Comments", ('user_id', 'item_id', 'comment', 'date'), user.id, self.id, comment_text, datetime.now())
        else:
            print("friend_state of {user} with owner of item: ".format(user=user), list(self.STATE.keys())[friend_state])
            print("comment permission for this item: ", list(self.STATE_TYPE.keys())[comment])
            print("{user} has no permission to comment for this item.".format(user=user))

        # TODO:
        # send notification to users who watches the item to watch

        try:
            users_watching = self.cur.execute(
                "select user_id from WatchRequests where item_id={item} and watch_method={wmethod}".format(item=self.id, wmethod=self.WATCH_REQUEST_TYPES["COMMENT"])).fetchall()
        except:
            users_watching = []
        for watcher in users_watching:
            self.insert("Notifications", ("sender", "receiver", "item_id", "notification_text", "notification_date"),
                        user.id, watcher.id, self.id,
                        "{user} commented for \'{item}\' item.".format(user=user, item=self),
                        datetime.now())
            print("Receiver :", watcher,
                  " Notification : ", "{user} commented for {owner} \'s \'{item}\' item.".format(owner=self.owner, user=user, item=self))

    def list_comments(self):
        fetched_comments = self.cur.execute(
            'select user_id, comment from Comments where item_id={item} order by datetime(date);'
                .format(item=self.id)).fetchall()
        return fetched_comments

    def rate(self, user, rating):
        self.cur.execute(
            'update Borrows set rate={rate} where item_id={item} and user_id ={user} and is_returned=1 ; '
                .format(user=user.id, item=self.id, rate=rating))
        db.connection.commit()

    def get_rating(self):
        avg_rating = self.cur.execute(
            'select avg(rate) from Borrows where item_id={item} and rate is not null;'
                .format(item=self.id)).fetchone()[0]
        return avg_rating

    def locate(self, location):
        self.cur.execute(
            "update Items set location=\'{loc}\' where id={id};".format(loc=location, id=self.id))
        db.connection.commit()

    def setstate(self, state_type, state):
        # print("update Items set {state_type}={state} where id={item}".format(item=self.id, state_type=state_type, state=self.STATE_TYPE[state]))
        self.__setattr__(state_type, state)
        self.cur.execute("update Items set {state_type}={state} where id={item};"
                         .format(item=self.id, state_type=state_type, state=self.STATE_TYPE[state]))
        db.connection.commit()
        if state_type is "borrow":
            try:
                users_watching = self.cur.execute(
                    "select user_id from WatchRequests where item_id={item} and watch_method={wmethod}".format(item=self.id,
                                                                                                               wmethod=
                                                                                                               self.WATCH_REQUEST_TYPES[
                                                                                                                   "BORROW"])).fetchall()
            except:
                users_watching = []
            for watcher in users_watching:
                self.insert("Notifications", ("sender", "receiver", "item_id", "notification_text", "notification_date"),
                            self.owner.id, watcher.id, self.id,
                            "{user} changed borrow permission for \'{item}\' item to {state}.".format(user=self.owner, item=self, state=state),
                            datetime.now())
                print("Receiver :", watcher,
                      " Notification : ",
                      "{user} changed borrow permission for \'{item}\' item to {state}.".format(user=self.owner, item=self, state=state))

    @classmethod
    def search(cls, user, search_text, genre, year=None, for_borrow=False):
        db_cur = db.get_cursor()
        words_text = list(search_text.split(" "))
        words = []
        for i in words_text:
            words.append("\'%" + i + "%\'")
        print(words)
        # in sqlite default like statement is case insensitive already
        if year:
            if for_borrow:
                f_string = f'SELECT owner, id ' + \
                           f'FROM Items WHERE ' + \
                           f'borrow!=0 and (borrow=3 or (owner in ' + \
                           f'(SELECT sender_user from Friends where receiver_user=? and Items.borrow>=state)  or ' + \
                           f'owner in (SELECT receiver_user from Friends where sender_user=? and Items.borrow>=state))) ' + \
                           f'and (({" or ".join(["artist like ?"] * len(words_text))}) or ' + \
                           f'({" or ".join(["title like ?"] * len(words_text))})) and datetime(year)>={"?"} '+\
                           f'and genre = \'%?%\' ;'
                data = [user.id]*2 + words + words + [year] + [genre]
                print(f_string, data)
                list_user_item = db_cur.execute(f_string, data).fetchall()

            else:

                f_string = f'SELECT owner, id ' + \
                           f'FROM Items WHERE ' + \
                           f'(({" or ".join(["artist like ?"] * len(words))}) or ' + \
                           f'({" or ".join(["artist like ?"] * len(words))})) and ' + \
                           f'datetime(year)>={"?"} and genre like \'%?%\' ;'
                data = words + words + [year] + [genre]
                print(f_string, data)
                list_user_item = db_cur.execute(f_string, data).fetchall()
                print(list_user_item)
        else:
            if for_borrow:
                f_string = f'SELECT owner, id ' + \
                           f'FROM Items WHERE ' + \
                           f'borrow!=0 and (borrow=3 or '+ \
                           f'(owner in (SELECT sender_user from Friends where receiver_user=? and Items.borrow>=state) or ' +\
                           f'owner in (SELECT receiver_user from Friends where sender_user=? and Items.borrow>=state))) ' +\
                           f'and (({" or ".join(["artist like ?"] * len(words_text))}) or ' +\
                           f'({" or ".join(["title like ?"] * len(words_text))})) and genre like \'%?%\' ;'
                # arkadaş değiller ama ödünç alma herkese açık
                data = [user.id]*2 + words + words + [genre]
                print(f_string, data)
                list_user_item = db_cur.execute(f_string, data).fetchall()
            else:
                f_string = f'SELECT owner, id' + \
                           f'FROM Items WHERE ' + \
                           f'(({" or ".join(["artist like ?"] * len(words_text))}) or ' + \
                           f'({" or ".join(["title like ?"] * len(words_text))})) and ' + \
                           f'genre like \'%?%\' ;'
                data = words + words + [genre]

                print(f_string,data)
                list_user_item = db_cur.execute(f_string, data).fetchall()
        return list_user_item

    def watch(self, user, watch_method):
        db.insert('WatchRequests', ('user_id', 'item_id', 'watch_method'), user.id, self.id, watch_method)

    def view(self, user):
        try:
            friend_state = self.cur.execute(
                "select state from Friends where (sender_user = {self_id} and receiver_user = {user_id}) or (sender_user = {user_id} and receiver_user = {self_id})"
                    .format(self_id=self.owner, user_id=user.id)).fetchone()[0]
        except:
            friend_state = 0
        if friend_state == self.STATE["NOFRIEND"]:
            sum_info = self.cur.execute(
                "select i.type, i.title, i.artist, i.genre from Items i where i.view = {state}"
                .format(state = 3)).fetchall()
        else:
            sum_info = self.cur.execute(
                "select i.type, i.title, i.artist, i.genre from Items i where i.view >= {state}"
                    .format(state=friend_state)).fetchall()
        result = []
        for info in sum_info:
            result.append(info[0])
        return result

    def detail(self, user):
        try:
            friend_state = self.cur.execute(
                "select state from Friends where (sender_user = {self_id} and receiver_user = {user_id}) or (sender_user = {user_id} and receiver_user = {self_id})"
                    .format(self_id=self.owner, user_id=user.id)).fetchone()[0]
        except:
            friend_state = 0
        if friend_state == self.STATE["NOFRIEND"]:
            detailed_info = self.cur.execute(
                "select * from Items i where i.detail = {state}"
                    .format(state=3)).fetchall()
        else:
            detailed_info = self.cur.execute(
                "select * from Items i where i.detail >= {state}"
                    .format(state=friend_state)).fetchall()
        result = []
        for info in detailed_info:
            result.append(info[0])
        return result

    def announce(self, owner_type, msg):
        db.insert("Announcements", ("item_id", "friend_type", "msg"), self.id, owner_type, msg)

    def delete(self):
        self.cur.execute("delete from Items where id = {item_id}".format(item_id=self.id))
        self.cur.execute("delete from BorrowRequests where item_id = {item_id}".format(item_id=self.id))
        self.cur.execute("delete from WatchRequests where item_id = {item_id} and (watch_method={breq} or watch_method={creq})"
                         .format(item_id=self.id, breq=self.WATCH_REQUEST_TYPES["BORROW"], creq=self.WATCH_REQUEST_TYPES['COMMENT']))
        db.connection.commit()

    def __repr__(self):
        return self.title

#
#
# user = _u.User("beste", "burhan", "beste.com", "password")
# user2 = _u.User("beste", "burhan", "bestee.com", "password")
# user3 = _u.User("beste", "burhan", "besteee.com", "password")
# user.friend("bestee.com")
# user2.friend("besteee.com")
# user.set_friend(user2, "CLOSEFRIEND")
# # user2.set_friend(user3, "FRIEND")
# it = Item(user, "type", "title", None, "artist", "genre", 1996)
# it2 = Item(user2, "type", "title", None, "artist", "genre", 1996)
# it3 = Item(user3, "type", "title", None, "artist", "genre", 1996)
# it4 = Item(user, "type", "title", None, "artist", "genre", 1996)
# it4.borrowed_req(user)
# it3.borrowed_by(user)
# it3.returned('lol')
# it4.locate('lololo')
# it2.setstate('view', 'EVERYONE')
# it3.setstate('borrow', 'CLOSED')
# it2.setstate('borrow', 'CLOSED')
# it4.setstate('borrow', 'CLOSED')
# it.setstate('borrow', 'CLOSED')
# it3.comment(user, "harikaaaaa")
# it3.comment(user, "harikaaaaaaaaa")
# it3.list_comments()
# it4.rate(user, 5)
# it3.get_rating()
# it3.search(user, "title", "genre", None, True)