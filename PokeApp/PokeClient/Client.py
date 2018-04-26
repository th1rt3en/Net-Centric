import socket
import json
import time
import sys
import os

from threading import Thread

TCP_IP = "127.0.0.1"
TCP_PORT = 9997

username = None
password = None

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((TCP_IP, TCP_PORT))
except socket.error:
    print "Failed to connect to server"
    print "Exiting"
    sys.exit()


def recv_msg():
    while True:
        try:
            data = sock.recv(1024)
        except socket.error:
            print "Server disconnected"
            sys.exit()
        try:
            msg = json.loads(data)
            if msg["cmd"].startswith("/exit"):
                print msg["msg"]
                print "Exiting"
                sys.exit()
            elif msg["cmd"].startswith("/login"):
                login()
            elif msg["cmd"].startswith("/register"):
                register()
            else:
                print msg["msg"]
        except ValueError:
            print "Indecipherable JSON"


def register():
    if raw_input("Would you like to register an account with this username ? [Y/N]").upper() in ("Y", "YES"):
        sock.send(format_msg(msg="/register"))
    else:
        print "Failed to login"
        print "Exiting"
        sys.exit()


def login():
    global username
    global password
    username = raw_input("Enter your username: ")
    password = raw_input("Enter your password: ")
    sock.send(format_msg(msg="/login"))


def format_msg(msg=""):
    return json.dumps({"username": username,
                       "password": password,
                       "msg": msg})


Thread(target=recv_msg, args=()).start()
