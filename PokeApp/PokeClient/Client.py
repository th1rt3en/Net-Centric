import json
import socket
import sys
import re
from threading import Thread
from multiprocessing.connection import Client

ADDRESS = ("127.0.0.1", 9999)

username = None
password = None
try:
    conn = Client(ADDRESS)
except socket.error:
    print "Failed to connect to server"
    print "Exiting"
    sys.exit()


def recv_msg():
    while True:
        try:
            data = conn.recv()
        except (socket.error, IOError):
            print "Disconnected from server"
            sys.exit()
        try:
            msg = json.loads(data)
            if msg["cmd"].startswith("/exit"):
                print msg["msg"]
                exit()
            elif msg["cmd"].startswith("/login"):
                login()
            elif msg["cmd"].startswith("/register"):
                register()
            elif msg["cmd"].startswith("/choose_game_mode"):
                choose_game_mode()
            elif msg["cmd"].startswith("/move"):
                move()
            elif msg["cmd"].startswith("/action"):
                action()
            elif msg["cmd"].startswith("/pick"):
                pick()
            else:
                print msg["msg"]
        except ValueError:
            print "Indecipherable JSON"
            print data
            exit()


def pick():
    choice = raw_input()
    r = re.findall(r"\D*(\d+)\D+(\d+)\D+(\d+)", choice)
    while not r:
        print "Invalid"
        choice = raw_input()
        r = re.findall(r"\D*(\d+)\D+(\d+)\D+(\d+)", choice)
    choice = [int(i) for i in r[0]]
    if len(list(set(choice))) == 3:
        send(choice)
    else:
        print "Invalid"
        pick()


def action():
    choice = int(raw_input())
    if choice == 1:
        send("/attack")
    elif choice == 2:
        num = raw_input("Choose the pokemon you want to switch to [1/2/3]")
        while num not in ("1", "2", "3"):
            print "Invalid"
        send("/switch" + num)
    elif choice == 3:
        send("/surrender")
    else:
        print "Invalid"
        action()


def send(msg):
    try:
        conn.send(format_msg(msg))
    except (socket.error, IOError):
        print "Disconnected from server"
        exit()


def exit():
    print "Exiting"
    sys.exit()


def move():
    direction = raw_input().upper()
    if direction in ("W", "A", "S", "D"):
        send("/move" + direction)
    elif direction in ("Q", "QUIT"):
        choose_game_mode()
    elif direction in ("L", "LIST"):
        send("/list")
    else:
        print "Invalid"
        move()


def choose_game_mode():
    choice = raw_input("Select a game mode\n"
                       "1. PokeCat\n"
                       "2. PokeBat\n"
                       "3. Exit\n").upper()
    if choice == "1":
        send("/pokecat")
    elif choice == "2":
        send("/pokebat")
    elif choice in ("3", "Q", "QUIT"):
        send("/exit")
        exit()
    else:
        print "Invalid"
        choose_game_mode()


def register():
    if raw_input("Would you like to register an account with this username ? [Y/N]").upper() in ("Y", "YES"):
        send("/register")
    else:
        send("/exit")
        print "Failed to login"
        print "Exiting"
        sys.exit()


def login():
    global username
    global password
    username = raw_input("Enter your username: ")
    password = raw_input("Enter your password: ")
    send("/login")


def format_msg(msg=""):
    return json.dumps({"username": username,
                       "password": password,
                       "msg": msg})


Thread(target=recv_msg, args=()).start()
