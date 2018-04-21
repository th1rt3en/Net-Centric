import socket
import json
import time
import sys
import os
import threading

from thread import start_new_thread
from threading import Thread
from SocketServer import ThreadingMixIn

TCP_IP = "127.0.0.1"
TCP_PORT = 9997
info = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))


def recv_msg(sock):
    while True:
        data = sock.recv(1024)
        try:
            msg = json.loads(data)
            if msg["cmd"].startswith("/login_success"):
                print msg["data"]
            elif msg["cmd"].startswith("/register"):
                if raw_input(msg["data"]).upper() in ("Y", "YES"):
                    sock.send(format_data(cmd="/register"))
                else:
                    print "Failed to log in. Exiting"
                    sys.exit()
            elif msg["cmd"].startswith("/exit"):
                print msg["data"]
                print "Exiting"
                sys.exit()
            else:
                print msg["data"]
        except ValueError:
            print "Indecipherable JSON"


def login(sock):
    if raw_input("Logging in as %s. Do you want to change account ? [Y/N]" % info["username"]).upper() in ("Y", "YES"):
        info["username"] = raw_input("Enter your username: ")
        info["password"] = raw_input("Enter your password: ")
        with open("Info.json", "w") as f:
            json.dump(info, f)
    sock.send(format_data(cmd="/login"))


def format_data(cmd="", data=""):
    return json.dumps({"username": info["username"],
                       "password": info["password"],
                       "cmd": cmd,
                       "data": data})


if not os.path.exists("Info.json"):
    info["username"] = raw_input("Enter your username: ")
    info["password"] = raw_input("Enter your password: ")
    with open("Info.json", "w") as f:
        json.dump(info, f)
else:
    with open("Info.json", "r") as f:
        info = json.load(f)

Thread(target=recv_msg, args=(sock,)).start()
login(sock)
