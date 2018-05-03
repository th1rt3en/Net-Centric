import re
import sys
import socket

from random import randint
from threading import Thread, Lock
from multiprocessing.connection import Listener

ADDRESS = ("", 9999)
NUMBER_OF_PLAYERS = 4
MAX_TURNS = 5

lock = Lock()
words = []
clients = []
current_word = ""
description = ""
revealed = ""
guessed = ""
count = 0


def whisper(from_username, to_username, msg):
    with lock:
        for client in clients[:]:
            if client[0] == to_username:
                client[1].send("Message from %s: " % from_username + msg)
                break


def out_of_turn():
    global count
    count += 1
    if count == NUMBER_OF_PLAYERS:
        game_end()


def get_new_word():
    global current_word
    global description
    global revealed
    global guessed
    global count
    guessed = ""
    count = 0
    current_word, description = words[randint(0, len(words)-1)]
    revealed = "".join(["-" if c != " " else " " for c in current_word])


def username_exists(username):
    with lock:
        for client in clients:
            if client[0] == username:
                return True
    return False


def broadcast(msg, username=None):
    global clients
    with lock:
        for client in clients[:]:
            if client[0] != username:
                try:
                    client[1].send(msg)
                except (socket.error, IOError):
                    print client[0], "disconnected"
                    clients = [c for c in clients if c[0] != client[0]]


def listener(username, conn, turn):
    global revealed
    with lock:
        if len(clients) < NUMBER_OF_PLAYERS:
            conn.send("Wait for more players")
    while True:
        try:
            guess = conn.recv()
            if guess.startswith("/all"):
                broadcast("Message from %s: " % username + re.match(r"/all (.*)", guess).group(1), username)
            elif guess.startswith("/tell"):
                result = re.match(r"/tell (\w+) (.*)", guess)
                whisper(username, result.group(1), result.group(2))
            else:
                match = check_guess(guess)
                if match and turn:
                    score(username, match*100)
                    with lock:
                        revealed = "".join(
                            [v if v != "-" else c if c.lower() == guess.lower() else "-" if c != " " else " " for c, v in
                             zip(current_word, revealed)])
                    conn.send("Right guess")
                    broadcast(revealed)
                    if revealed == current_word:
                        score(username, 400)
                        game_end()
                elif not turn:
                    conn.send("You have no turn left")
                    conn.send("/sleep")
                else:
                    turn -= 1
                    conn.send("Wrong guess")
                    conn.send("You have %d turns left" % turn)
                    conn.send("/sleep")
                    if turn < 1:
                        out_of_turn()
        except (socket.error, IOError, EOFError):
            print username, "disconnected"
            sys.exit()


def check_guess(guess):
    global guessed
    if guess.lower() in guessed:
        return 0
    else:
        guessed += guess.lower()
    return sum(char.lower() == guess.lower() for char in current_word)


def score(username, score):
    with lock:
        for client in clients:
            if client[0] == username:
                client[2] += score
                break


def game_start():
    while True:
        if len(clients) == NUMBER_OF_PLAYERS:
            get_new_word()
            broadcast("The game is starting")
            broadcast(revealed)
            broadcast("Description: " + description)
            broadcast("/start")
            break
    sys.exit()


def game_end():
    winner = max(clients, key=lambda x: x[2])
    broadcast("The game has ended")
    with lock:
        while clients:
            client = clients.pop(0)
            if client[0] != winner[0]:
                client[1].send("Lost")
            else:
                client[1].send("Won")
            client[1].send("/exit")
    Thread(target=game_start, args=()).start()


try:
    with open("words.txt", "r") as f:
        for (word, description) in re.findall(r"([\w ]+)\t([\w ]+)", f.read()):
            words.append((word, description))
except IOError:
    print "words.txt not found"
    sys.exit()

tcp_server = Listener(ADDRESS)
Thread(target=game_start, args=()).start()

while True:
    conn = tcp_server.accept()
    print "connection from", tcp_server.last_accepted
    username = conn.recv()
    if username_exists(username):
        conn.send("Username already exists. Choose another username and try again.")
        conn.close()
    else:
        clients.append([username, conn, 0])
        Thread(target=listener, args=(username, conn, MAX_TURNS)).start()
