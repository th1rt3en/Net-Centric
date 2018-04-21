import os
import re
import sys
import json
import time
import socket
import urllib2
import threading

from threading import Thread
from SocketServer import ThreadingMixIn
from bs4 import BeautifulSoup
from Pokemon import Pokemon
from Player import Player
from contextlib import closing
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.support.ui import WebDriverWait


class ClientThread(Thread):

    def __init__(self, conn, ip, port):
        Thread.__init__(self)
        self.conn = conn
        self.ip = ip
        self.port = port
        print "Started thread for %s:%d" % (ip, port)

    def run(self):
        while True:
            data = self.conn.recv(1024)
            try:
                msg = json.loads(data)
                if msg["cmd"].startswith("/login"):
                    """Handle user login and register"""
                    cmd, data = self.authenticate(msg["username"], msg["password"])
                    self.conn.send(self.format_data(cmd, data))
                    if cmd.startswith("/register"):
                        response = json.loads(self.conn.recv(1024))
                        if response["cmd"].startswith("/register"):
                            player = Player({"username": response["username"], "password": response["password"]})
                            with open("Info.json", "r+") as f:
                                players = [Player(p) for p in json.load(f)]
                                players.append(player)
                                f.seek(0)
                                json.dump([player.serialize() for player in players], f, indent=4, separators=(",", ": "))
                                f.truncate()
                            self.conn.send(self.format_data(data="Successfully registered as %s\nWelcome to PokeServer" % player.username))
                    else:
                        pass
            except ValueError:
                print "Indecipherable JSON"

    @staticmethod
    def format_data(cmd="", data=""):
        return json.dumps({"cmd": cmd,
                           "data": data})

    @staticmethod
    def authenticate(username, password):
        if not os.path.exists("Info.json"):
            with open("Info.json", "w") as f:
                json.dump({}, f)
        with open("Info.json", "r") as f:
            players = [Player(player) for player in json.load(f)]
        player = filter(lambda x: x.username == username, players)
        if len(player):
            if player[0].password == password:
                return "/login_success", "Welcome to PokeServer"
            else:
                return "/exit", "Wrong password"
        else:
            return "/register", "User does not exit. Would you like to create an account with this username ? [Y/N]"


#   End of ClientThread


TCP_IP = "127.0.0.1"
TCP_PORT = 9997
BUFFER_SIZE = 1024

print "Starting server"

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind((TCP_IP, TCP_PORT))
threads = []
pokedex = []

print "Looking for Pokedex"
if not os.path.exists("Pokedex.json"):
    print "Pokedex not found"
    print "Getting Pokedex"
    option = ChromeOptions()
    option.add_argument("headless")
    with closing(Chrome("chromedriver.exe", chrome_options=option)) as browser:
        browser.get("https://www.pokedex.org/")
        number_of_pokemons = browser.execute_script(
            "return document.getElementById('monsters-list').getElementsByTagName('li').length")
        print "Found %d Pokemons" % number_of_pokemons
        print "Downloading info..."
        for id in range(1, number_of_pokemons + 1):
            browser.get("https://www.pokedex.org/#/pokemon/" + str(id))
            WebDriverWait(browser, 5).until(lambda x: x.execute_script(
                "return document.getElementsByClassName('detail-national-id')[0].children[0].innerHTML")[1:] == str(id))
            info = {"id": id}
            info["name"] = browser.execute_script(
                "return document.getElementsByClassName('detail-panel-header')[0].innerHTML")
            info["hp"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[0].children[1].innerHTML"))
            info["atk"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[1].children[1].innerHTML"))
            info["dfs"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[2].children[1].innerHTML"))
            info["spd"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[3].children[1].innerHTML"))
            info["sp_atk"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[4].children[1].innerHTML"))
            info["sp_dfs"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[5].children[1].innerHTML"))
            pokemon = Pokemon(info)
            pokedex.append(pokemon)
            print "Downloaded %d/%d Pokemons" % (id, number_of_pokemons)
        with open("Pokedex.json", "w") as f:
            json.dump([pokemon.serialize() for pokemon in pokedex], f, sort_keys=True, indent=4,
                      separators=(",", ": "))
        print "Finished downloading"
else:
    print "Pokedex found"
    with open('Pokedex.json', 'r') as f:
        pokedex = [Pokemon(info) for info in json.load(f)]
print "Pokedex up to date"

print "Server is up"
while True:
    try:
        tcp_server.listen(1)
        conn, (ip, port) = tcp_server.accept()
        new_thread = ClientThread(conn, ip, port)
        new_thread.start()
        threads.append(new_thread)
    except KeyboardInterrupt:
        print "Server stopped"

for t in threads:
    t.join()
