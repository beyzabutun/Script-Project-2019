from socket import socket, AF_INET, SOCK_STREAM
from concurrent.futures import ThreadPoolExecutor as TPE
from typing import List, Tuple
from random import randint
import create_tables
import user
import item
from time import sleep
import database
import sqlite3
import pickle
import threading
from threading import Thread


class Server:
    request_port = 21455
    notification_port = 12510
    notification_waiting_clients = dict()
    notification_sock = socket(AF_INET, SOCK_STREAM)

    meta_data = {
        'user': {
            'sign_up': user.User.sign_up,
            'login': user.User.login,
            'verify': user.User.verify,
            'change_password': user.User.change_password,
            'friend' : user.User.friend,
            'set_friend' : user.User.set_friend,
            'lookup': user.User.look_up,
            'list_items': user.User.list_items,
            'watch': user.User.watch
        },
        'item': {

        }

    }

    @classmethod
    def send_notification(cls, notification_msg: str, user_id):
        # if uid in cls.notification_waiting_clients:
        print(notification_msg)
        notification_msg = pickle.dumps(notification_msg)
        print(cls.notification_waiting_clients[user_id])
        cls.notification_waiting_clients[user_id].send(notification_msg)

    @classmethod
    def notification_handler(cls, notification_sock, addr: Tuple):
        user_id = notification_sock.recv(128)
        user_id = pickle.loads(user_id)
        print(f'A Client is registered to be notified with user id : {user_id} with address: {addr}')

        print(threading.current_thread().ident)
        cls.notification_waiting_clients[user_id] = notification_sock
        # cls.send_notification("hola", user_id)

    @classmethod
    def request_handler(cls, request_sock):
        print('Request Handler is started')
        db = sqlite3.connect('data.db')
        database_obj = database.DBConnection(db, db.cursor())
        while True:
            print(request_sock)
            print(threading.current_thread().ident)
            request = request_sock.recv(1024)
            print("after taking params", request)

            if request == b'':
                print('empty req. aborting.')
                break

            request_type = pickle.loads(request)
            print(request_type[0])

            if request_type[0] not in cls.meta_data['user'] and request_type[0] not in cls.meta_data['item'] :
                print('no req')
                continue

            print(request_type)
            if request_type[0] in cls.meta_data['user']:
                func = cls.meta_data['user'][request_type[0]]
                if request_type[0] != 'login' and request_type[0] != 'sign_up':
                    msg = func(client, database_obj, request_type[1:])
                    msg = pickle.dumps(msg)
                else:
                    msg = func(database_obj, request_type[1:])
                    if msg[0] == '+':
                        client = user.User(database_obj, email=request_type[1], password=request_type[2])
                    msg = pickle.dumps(msg)
            else:
                func = cls.meta_data['item'][request_type[0]]
                if request_type[0] != 'add_item':
                    msg = func(item, database_obj, request_type[1:])
                    msg = pickle.dumps(msg)
                else:   # add item
                    msg = func(database_obj, request_type[1:])
                    if msg[0] == '+':
                        item = item.Item(database_obj, msg[1])
                    msg = pickle.dumps(msg)

            print(request_type[1:])
            print("return from ", request_type[0], 'msg', msg)
            request_sock.send(msg)

        db.close()

    @classmethod
    def start_server(cls):
        try:
            request_handler_sock = socket(AF_INET, SOCK_STREAM)
            request_handler_sock.bind(('', cls.request_port))
            request_handler_sock.listen()
        except Exception as e:
            print(f'request->{e !r}')
            return
        while True:

            conn, peer = request_handler_sock.accept()
            print("conn ", conn)
            req_handler = Thread(target=cls.request_handler, args=(conn,))
            req_handler.start()
            print("New client -> thread : ", req_handler.ident)

    @classmethod
    def start_notification(cls):
        try:
            notification_handler_sock = socket(AF_INET, SOCK_STREAM)
            notification_handler_sock.bind(('', cls.notification_port))
            notification_handler_sock.listen()
        except Exception as e:
            print(f'notify->{e !r}')
            return

        while True:
            conn, peer = notification_handler_sock.accept()
            not_handler = Thread(target=cls.notification_handler, args=(conn, peer))
            not_handler.start()
            print("Notification thread -> ", not_handler.ident)


    @classmethod
    def start(cls):

        start_server = Thread(target=cls.start_server)
        start_server.start()
        start_notification = Thread(target=cls.start_notification)
        start_notification.start()
        #
        # start_server.join()
        # start_notification.join()

if __name__ == "__main__":
    server = Server()
    pool = server.start()

    # pool.shutdown(wait=True)
