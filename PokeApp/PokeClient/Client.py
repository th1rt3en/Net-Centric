import json
import socket
import sys
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
                exit()
            elif msg["cmd"].startswith("/login"):
                login()
            elif msg["cmd"].startswith("/register"):
                register()
            elif msg["cmd"].startswith("/choose_game_mode"):
                choose_game_mode()
            elif msg["cmd"].startswith("/move"):
                move()
            else:
                print msg["msg"]
        except ValueError:
            print "Indecipherable JSON"


def exit():
    print "Exiting"
    sys.exit()


def move():
    direction = raw_input("Choose a direction [W/A/S/D] to move\n"
                          "Enter 'list' to see your current pokemons\n"
                          "Enter 'q' or 'quit' to exit\n").upper()
    if direction in ("W", "A", "S", "D"):
        sock.send(format_msg(msg="/move" + direction))
    elif direction in ("Q", "QUIT"):
        choose_game_mode()
    else:
        print "Invalid"
        move()


def choose_game_mode():
    choice = raw_input("Select a game mode\n"
                       "1. PokeCat\n"
                       "2. PokeBat\n"
                       "3. Exit\n").upper()
    if choice == "1":
        sock.send(format_msg(msg="/pokecat"))
    elif choice == "2":
        sock.send(format_msg(msg="/pokebat"))
    elif choice in ("3", "Q", "QUIT"):
        sock.send(format_msg(msg="/exit"))
        exit()
    else:
        print "Invalid"
        choose_game_mode()


def register():
    if raw_input("Would you like to register an account with this username ? [Y/N]").upper() in ("Y", "YES"):
        sock.send(format_msg(msg="/register"))
    else:
        sock.send(format_msg(msg="/exit"))
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
