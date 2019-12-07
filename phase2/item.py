from isbnlib import meta
from datetime import datetime, timedelta


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

    def __init__(self, database_obj, item_id):
        self.cur = database_obj.curs
        item_query = self.cur.execute("select * from Items where id = {id}".format(id=item_id)).fetchone()
        self.id = item_query[0]
        self.owner = item_query[1]
        self.type = item_query[2]
        self.title = item_query[3]
        self.uniqid = item_query[4]
        self.artist = item_query[5]
        self.genre = item_query[6]
        self.year = item_query[7]
        self.location = item_query[8]
        self.view = item_query[9]
        self.detail = item_query[10]
        self.borrow = item_query[11]
        self.comment = item_query[12]
        self.search = item_query[13]

    @classmethod
    def add_item(cls, database_obj, owner, params):
        item_type, title, uniqid, artist, genre, year = params
        print("add_item: ", owner, item_type, title)
        is_verified = False
        try:
            is_verified = database_obj.curs.execute('select is_verified from Users where id=?', (owner.id,)).fetchone()[
                0]
        except:
            return "There is no such user."
        if not is_verified:
            return "Owner is not verified, item can't be created!"
        else:
            user_id = database_obj.curs.execute("select id from Users where email like \'{m}\'".format(m=owner.email))
            user_id = user_id.fetchone()[0]
            item_type = item_type
            genre = genre
            location = None
            view = 2
            borrow = 2
            detail = 2
            comment = 2
            search = 2
            if uniqid is '':
                title = title
                artist = artist
                year = year
                database_obj.insert("Items", ('owner', 'type', 'title', 'uniqueid', 'artist', 'genre', 'year', 'view',
                                              'detail', 'search', 'borrow', 'comment'), user_id, item_type, title,
                                    uniqid, artist, genre, year, 2, 2, 2, 2, 2)
                id = database_obj.curs.execute("select last_insert_rowid()").fetchone()[0]
                return " item is created."
            else:
                metadata = None
                try:
                    metadata = meta(isbn=uniqid)
                except Exception as ex:
                    print(ex)
                if metadata is not None:
                    title = metadata['Title']
                    year = metadata['Year']
                    artist = metadata['Authors'][0]
                    database_obj.insert("Items",
                                        ('owner', 'type', 'title', 'uniqueid', 'artist', 'genre', 'year', 'view',
                                         'detail', 'search', 'borrow', 'comment'), user_id,
                                        item_type, title, uniqid, artist, genre, year, 2, 2, 2, 2, 2)
                    id = database_obj.curs.execute("select last_insert_rowid()").fetchone()[0]
                    return " item is created with isbn number :'{uid}'".format(uid=uniqid)

            # TODO
            # if there is a user who watches owner, send notification followed users
            try:
                users_watching = database_obj.curs.execute(
                    "select user_id from WatchRequests where followed_id={owner} and watch_method={wmethod}".format(
                        owner=owner.id, wmethod=cls.WATCH_REQUEST_TYPES["USER"])).fetchall()
            except:
                users_watching = []

            if not users_watching:
                return
            for user in users_watching[0]:
                database_obj.insert("Notifications",
                                    ("sender", "receiver", "item_id", "notification_text", "notification_date"),
                                    owner.id, user, database_obj.id,
                                    "{owner} add new item : \'{item}\' .".format(owner=owner, item=title),
                                    datetime.now())
                print("Receiver :  ", user, " Notification : ",
                      "{owner} add new item :\'{item}\' .".format(owner=owner, item=title))

    def borrowed_req(self, database_obj, user, params):
        cur = database_obj.curs
        already_requested = None
        try:
            already_requested = cur.execute("select user_id from BorrowRequests where item_id={item} and user_id={user}".format(item=self.id, user=user.id)).fetchone()[0]
        except:
            database_obj.insert("BorrowRequests", ('user_id', 'item_id', 'request_date'), user.id, self.id, datetime.now())
        if already_requested is not None: # true
            print("{user} already requested for this item.".format(user=user))
        queue = cur.execute("select count(*) from BorrowRequests where item_id={self_id}"
                                 .format(self_id = self.id)).fetchone()[0]

        return "'{user}' Your place in borrow request list: '{queue}'".format(user=user, queue=queue)

    def borrowed_by(self, database_obj, params):
        email, return_date = params
        if return_date == '':
            return_date = 2
        cur = database_obj.curs
        taking_date = datetime.now()
        return_date = taking_date + timedelta(weeks=return_date)
        query = self.cur.execute("select id, name from Users where email = \'{email}\'".format(email=email)).fetchone()
        user_id = query[0]
        name = query[1]

        already_borrowed = None
        try:
            already_borrowed = cur.execute(f"select id from Borrows where is_returned=0 and item_id={'?'}", [self.id]).fetchone()[0]

        except:
            database_obj.insert("Borrows", ('user_id', 'item_id', 'taking_date', 'return_date', 'is_returned'), user_id,
                      self.id, datetime.now(), return_date, 0)
            cur.execute('delete from BorrowRequests where user_id={user} and item_id={item} ;'
                             .format(user=user_id, item=self.id ))
            database_obj.conn.commit()
        if already_borrowed is not None:
            return "This item already borrowed."
        return "'{name}' borrowed the item: '{id}'".format(id=name, id=self.id)

    def returned(self, database_obj, location=None):
        self.cur.execute("update Borrows set is_returned=1 where is_returned=0 and item_id={id};".format(id=self.id))
        self.location = location
        self.cur.execute("update Items set location=\'{loc}\' where id={id};".format(loc=location, id=self.id))
        # TODO:
        # send notification to users who watches the item to borrow
        # delete watchrequest after notification
        database_obj.conn.commit()
        try:
            users_watching = self.cur.execute(
                "select user_id from WatchRequests where item_id={item} and watch_method={wmethod}"
                    .format(item=self.id, wmethod=self.WATCH_REQUEST_TYPES["BORROW"])).fetchall()
            self.cur.execute(
                "delete from WatchRequests where item_id={item} and  watch_method={wmethod}"
                    .format(item=self.id, wmethod=self.WATCH_REQUEST_TYPES["BORROW"]))
            database_obj.conn.commit()
        except:
            users_watching = []
        if users_watching == []:
            return
        for user in users_watching[0]:
            db.insert("Notifications",
                        ("sender", "receiver", "item_id", "notification_text", "notification_date"),
                        self.owner.id, user, self.id,
                        " \'{item}\' item is returned.".format(item=self),
                        datetime.now())
            print("Receiver :  ", user, " Notification : ", " \'{item}\' item is returned.".format(item=self))

    def make_comment(self, user, comment_text):
        try:
            friend_state = self.cur.execute(
                "select state from Friends where (sender_user = {self_id} and receiver_user = {user_id}) or (sender_user = {user_id} and receiver_user = {self_id})"
                    .format(self_id=self.owner.id, user_id=user.id)).fetchone()[0]
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
            return

        # TODO:
        # send notification to users who watches the item to watch

        try:
            users_watching = self.cur.execute(
                "select user_id from WatchRequests where item_id={item} and watch_method={wmethod}".format(item=self.id, wmethod=self.WATCH_REQUEST_TYPES["COMMENT"])).fetchall()
        except:
            users_watching = []
        if users_watching==[]:
            return
        for watcher in users_watching[0]:
            db.insert("Notifications", ("sender", "receiver", "item_id", "notification_text", "notification_date"),
                        user.id, watcher, self.id,
                        "{user} commented for \'{item}\' item.".format(user=user, item=self),
                        datetime.now())
            print("Receiver :", watcher,
                  " Notification : ", "{user} commented for {owner}\'s \'{item}\' item.".format(owner=self.owner, user=user, item=self))

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
            if users_watching==[]:
                return
            for watcher in users_watching[0]:
                db.insert("Notifications", ("sender", "receiver", "item_id", "notification_text", "notification_date"),
                            self.owner.id, watcher, self.id,
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
            words.append("%" + i + "%")
        # in sqlite default like statement is case insensitive already
        if year:
            if for_borrow:
                f_string = f'SELECT owner, id ' + \
                           f'FROM Items WHERE ' + \
                           f'borrow!=0 and (borrow=3 or (owner in ' + \
                           f'(SELECT sender_user from Friends where receiver_user={"?"}  and Items.borrow>=state)  or ' + \
                           f'owner in (SELECT receiver_user from Friends where sender_user={"?"}  and Items.borrow>=state))) ' + \
                           f'and (({" or ".join(["artist like ?"] * len(words_text))}) or ' + \
                           f'({" or ".join(["title like ?"] * len(words_text))})) and datetime(year)>={"?"} '+\
                           f'and genre = {"?"} ;'
                data = [user.id]*2 + words + words + [year] + [ genre]
                list_user_item = db_cur.execute(f_string, data).fetchall()

            else:

                f_string = f'SELECT owner, id ' + \
                           f'FROM Items WHERE ' + \
                           f'(({" or ".join(["artist like ?"] * len(words))}) or ' + \
                           f'({" or ".join(["artist like ?"] * len(words))})) and ' + \
                           f'datetime(year)>={"?"} and genre = {"?"} ;'
                data = words + words + [year] + [genre]
                list_user_item = db_cur.execute(f_string, data).fetchall()
        else:
            if for_borrow:
                f_string = f'SELECT owner, id ' + \
                           f'FROM Items WHERE ' + \
                           f'borrow!=0 and (borrow=3 or ' + \
                           f'(owner in (SELECT sender_user from Friends where receiver_user={"?"} and Items.borrow>=state) or ' +\
                           f'owner in (SELECT receiver_user from Friends where sender_user={"?"}  and Items.borrow>=state))) ' +\
                           f'and (({" or ".join(["artist like ?"] * len(words_text))}) or ' +\
                           f'({" or ".join(["title like ?"] * len(words_text))})) and genre = {"?"} ;'
                # arkadaş değiller ama ödünç alma herkese açık
                data = [user.id]*2 + words + words + [genre]
                list_user_item = db_cur.execute(f_string, data).fetchall()
            else:
                f_string = f'SELECT  owner, id  ' + \
                           f'FROM Items WHERE ' + \
                           f'(({" or ".join(["artist like ?"] * len(words))}) or ' + \
                           f'({" or ".join(["title like ?"] * len(words))})) and ' + \
                           f'genre = {"?"} ;'
                data = words + words + [genre]
                list_user_item = db_cur.execute(f_string, data).fetchall()
        return list_user_item

    def watch(self, user, watch_method):
        db.insert('WatchRequests', ('user_id', 'item_id', 'watch_method'), user.id, self.id, self.WATCH_REQUEST_TYPES[watch_method])

    def view_info(self, user):
        # try:
        #     friend_state = self.cur.execute(
        #         "select state from Friends where (sender_user = {self_id} and receiver_user = {user_id}) or (sender_user = {user_id} and receiver_user = {self_id})"
        #             .format(self_id=self.owner, user_id=user.id)).fetchone()[0]
        # except:
        #     friend_state = 0
        # print(friend_state)
        # if friend_state == self.STATE["NOFRIEND"]:
        #     sum_info = self.cur.execute(
        #         "select i.type, i.title, i.artist, i.genre from Items i where i.view = {state}"
        #         .format(state = 3)).fetchall()
        # else:
        #     sum_info = self.cur.execute(
        #         "select i.type, i.title, i.artist, i.genre from Items i where i.view >= {state}"
        #             .format(state=friend_state)).fetchall()
        #
        # return sum_info
        try:
            friend_state = self.cur.execute(
                "select state from Friends where (sender_user = {self_id} and receiver_user = {user_id}) or (sender_user = {user_id} and receiver_user = {self_id})"
                    .format(self_id=self.owner.id, user_id=user.id)).fetchone()[0]
        except:
            friend_state = 0
        view = self.cur.execute(
                "select i.view from Items i where i.id={item}"
                .format(item=self.id)).fetchone()[0]

        if (view >= friend_state and friend_state is not 0) or (view is 3):
            sum_info = self.cur.execute(
                     "select type, title, artist, genre from Items where id = {id}"
                .format(id=self.id)).fetchall()
            return sum_info

        else:
            print("friend_state of {user} with owner of item: ".format(user=user), list(self.STATE.keys())[friend_state])
            print("view permission for this item: ", list(self.STATE_TYPE.keys())[view])
            print("{user} has no permission to view summary information of this item.".format(user=user))


    def detailed_info(self, user):
        try:
            friend_state = self.cur.execute(
                "select state from Friends where (sender_user = {self_id} and receiver_user = {user_id}) or (sender_user = {user_id} and receiver_user = {self_id})"
                    .format(self_id=self.owner.id, user_id=user.id)).fetchone()[0]
        except:
            friend_state = 0
        detail = self.cur.execute(
                "select i.detail from Items i where i.id={item}"
                .format(item=self.id)).fetchone()[0]

        if (detail >= friend_state and friend_state is not 0) or (detail is 3):
            detailed_info = self.cur.execute(
                "select i.owner, i.type, i.title, i.artist, i.genre, i.year, i.location from Items i where i.id = {self_id}"
                    .format(self_id=self.id)).fetchall()
            return detailed_info

        else:
            print("friend_state of {user} with owner of item: ".format(user=user), list(self.STATE.keys())[friend_state])
            print("detail permission for this item: ", list(self.STATE_TYPE.keys())[detail])
            print("{user} has no permission to view detailed information of this item.".format(user=user))


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

