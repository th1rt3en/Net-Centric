import sys
import socket

from time import sleep
from threading import Thread
from multiprocessing.connection import Client


def listener(conn):
    while True:
        try:
            msg = conn.recv()
            if msg.startswith("/sleep"):
                cmd_q.append("sleep(5)")
            elif msg.startswith("/start"):
                Thread(target=guess, args=(conn,)).start()
            elif msg.startswith("/exit"):
                cmd_q.append("sys.exit()")
                sys.exit()
            else:
                print msg
        except (socket.error, IOError, EOFError):
            print "Disconnected from server"
            cmd_q.append("sys.exit()")
            sys.exit()


def guess(conn):
    while True:
        if cmd_q:
            eval(cmd_q.pop(0))
        else:
            guess = raw_input("Enter your guess\n"
                              "Send message to all players using /all [msg]\n"
                              "Send private message to other players using /tell [username] [msg]\n")
            while len(guess) != 1 and not guess.startswith("/all") and not guess.startswith("/tell"):
                print "Invalid"
                guess = raw_input("Enter your guess\n"
                                  "Send message to all players using /all [msg]\n"
                                  "Send private message to other players using /tell [username] [msg]\n")
            if len(guess) == 1:
                cmd_q.append("sleep(5)")
            try:
                conn.send(guess)
            except (socket.error, IOError):
                print "Disconnected from server"
                cmd_q.append("sys.exit()")
                sys.exit()


ADDRESS = ("127.0.0.1", 9999)

cmd_q = []
username = raw_input("Enter your username: ")

conn = Client(ADDRESS)
conn.send(username)

Thread(target=listener, args=(conn,)).start()
