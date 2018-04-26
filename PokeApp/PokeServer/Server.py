import os
import re
import sys
import json
import time
import socket
import urllib2
import threading

from Queue import Queue
from time import sleep
from threading import Thread
from random import randint
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
        self.conn.send(self.format_msg(cmd="/login"))
        while True:
            try:
                data = self.conn.recv(1024)
            except socket.error:
                print "Client disconnected"
                sys.exit()
            try:
                print data
                msg = json.loads(data)
                if msg["msg"].startswith("/login"):
                    """User login"""
                    cur_player = Player({"username": msg["username"], "password": msg["password"]})
                    if not os.path.exists("Info.json"):
                        open("Info.json", "w").close()
                    with open("Info.json", "r") as f:
                        players = [Player(player) for player in json.load(f)]
                        if any(player.username == cur_player.username and player.password == cur_player.password for player in players):
                            self.conn.send(self.format_msg(msg="Welcome to PokeServer"))
                        elif any(player.username == cur_player.username for player in players):
                            self.conn.send(self.format_msg(msg="Wrong password"))
                            self.conn.send(self.format_msg(cmd="/login"))
                        else:
                            self.conn.send(self.format_msg(msg="Username not in use."))
                            self.conn.send(self.format_msg(cmd="/register"))

                elif msg["msg"].startswith("/register"):
                    """User register"""
                    cur_player = Player({"username": msg["username"], "password": msg["password"]})
                    self.register(cur_player)
                    self.conn.send(self.format_msg(msg="Successfully registered"))
                    self.conn.send(self.format_msg(msg="Welcome to PokeServer"))

            except ValueError:
                print "Indecipherable JSON"

    @staticmethod
    def register(player):
        with open("Info.json", "r+") as f:
            players = [Player(p) for p in json.load(f)]
            players.append(player)
            f.seek(0)
            json.dump([player.serialize() for player in players], f, indent=4,
                      separators=(",", ": "))
            f.truncate()

    @staticmethod
    def format_msg(cmd="", msg=""):
        return json.dumps({"cmd": cmd,
                           "data": msg})


#   End of ClientThread

TCP_IP = "127.0.0.1"
TCP_PORT = 9997
BUFFER_SIZE = 1024
WORLD_SIZE = 1000
NUMBER_OF_POKEMONS_PER_SPAWN = 50
TIME_BETWEEN_SPAWNS = 60
TIME_UNTIL_DESPAWN = 300

print "Starting server"

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind((TCP_IP, TCP_PORT))
threads = []
pokedex = []
world = []
despawn_q = []


def random_points(number_of_points):
    points = []
    global world
    global WORLD_SIZE
    while number_of_points:
        x = randint(0, WORLD_SIZE-1)
        y = randint(0, WORLD_SIZE-1)
        if not world[x][y] and (x, y) not in points:
            points.append((x, y))
            number_of_points -= 1
    return points


def spawn_pokemons(number, delay):
    sleep(0.1)
    print "Spawning %d Pokemons a minute" % number
    global world
    global pokedex
    global despawn_q
    while True:
        sleep(delay)
        points = random_points(number)
        despawn_q.append(points)
        for (x, y) in points:
            world[x][y] = Pokemon(pokedex[randint(0, len(pokedex)-1)].serialize())
        with open("World.json", "w") as f:
            json.dump(world, f, indent=4, default=lambda p: p.serialize())
        with open("Despawn.json", "w") as f:
            json.dump(despawn_q, f, indent=4)
        print "Spawned %d Pokemons" % number


def despawn_pokemons(second):
    sleep(0.2)
    print "Despawning pokemons every %.2f minutes" % (second / 60.0)
    global despawn_q
    global world
    while True:
        if despawn_q:
            sleep(second)
            points = despawn_q.pop(0)
            for (x, y) in points:
                world[x][y] = 0
            with open("World.json", "w") as f:
                json.dump(world, f, indent=4, default=lambda p: p.serialize())
            with open("Despawn.json", "w") as f:
                json.dump(despawn_q, f, indent=4)
            print "Despawned"


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
            WebDriverWait(browser, 10).until(lambda x: x.execute_script(
                "return document.getElementsByClassName('detail-national-id')[0].children[0].innerHTML")[1:] == str(id))
            info = {"id": id}
            info["name"] = browser.execute_script(
                "return document.getElementsByClassName('detail-panel-header')[0].innerHTML")
            number_of_types = browser.execute_script(
                "return document.getElementsByClassName('detail-types')[0].children.length")
            info["type"] = [browser.execute_script(
                "return document.getElementsByClassName('detail-types')[0].children[%d].innerHTML" % d) for d in
                range(number_of_types)]
            info["base_hp"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[0].children[1].innerHTML"))
            info["base_atk"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[1].children[1].innerHTML"))
            info["base_def"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[2].children[1].innerHTML"))
            info["base_speed"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[3].children[1].innerHTML"))
            info["base_special_atk"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[4].children[1].innerHTML"))
            info["base_special_def"] = int(
                browser.execute_script("return document.getElementsByClassName('stat-bar')[5].children[1].innerHTML"))
            info["dmg_when_atked"] = [{"type": browser.execute_script(
                "return document.getElementsByClassName('when-attacked')[0].children[%d].children[0].innerHTML" % i),
                "multiply": float(browser.execute_script(
                    "return document.getElementsByClassName('when-attacked')[0].children[%d].children[1].innerHTML" % i)[
                                  :-1])}
                for i in range(int(browser.execute_script(
                    "return document.getElementsByClassName('when-attacked')[0].children.length")))
                if len(browser.execute_script(
                    "return document.getElementsByClassName('when-attacked')[0].children[%d].children[0].innerHTML" % i))]
            info["dmg_when_atked"].extend([{"type": browser.execute_script(
                "return document.getElementsByClassName('when-attacked')[0].children[%d].children[2].innerHTML" % i),
                "multiply": float(browser.execute_script(
                    "return document.getElementsByClassName('when-attacked')[0].children[%d].children[3].innerHTML" % i)[
                                  :-1])}
                for i in range(int(browser.execute_script(
                    "return document.getElementsByClassName('when-attacked')[0].children.length")))
                if len(browser.execute_script(
                    "return document.getElementsByClassName('when-attacked')[0].children[%d].children[2].innerHTML" % i))])
            pokemon = Pokemon(info)
            pokedex.append(pokemon)
            print "Downloaded %d/%d Pokemons" % (id, number_of_pokemons)
    with closing(Chrome("chromedriver.exe", chrome_options=option)) as browser:
        print "Downloading base experience"
        browser.get("https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_effort_value_yield")
        for i in range(int(browser.execute_script("return document.getElementsByTagName('tbody')[0].children.length"))):
            id = browser.execute_script(
                "return document.getElementsByTagName('tbody')[0].children[%d].children[0].children[0].innerHTML" % i)
            if re.match(r"\d+[a-zA-Z]+", id):
                continue
            id = int(id)
            if id > len(pokedex):
                break
            pokedex[id - 1].base_experience = browser.execute_script(
                "return document.getElementsByTagName('tbody')[0].children[%d].children[3].innerHTML" % i).strip()
    with open("Pokedex.json", "w") as f:
        json.dump([pokemon.serialize() for pokemon in pokedex], f, indent=4, separators=(",", ": "))
    print "Finished downloading"
else:
    print "Pokedex found"
    with open('Pokedex.json', 'r') as f:
        pokedex = [Pokemon(info) for info in json.load(f)]
print "Pokedex up to date"

print "Loading PokeWorld"
if not os.path.exists("World.json"):
    world = [[0] * WORLD_SIZE for _ in range(WORLD_SIZE)]
    with open("World.json", "w") as f:
        json.dump(world, f, indent=4)
else:
    with open("World.json", "r") as f:
        world = [[Pokemon(item) if item else item for item in line] for line in json.load(f)]
print "Done loading PokeWorld"

Thread(target=spawn_pokemons, args=(NUMBER_OF_POKEMONS_PER_SPAWN, TIME_BETWEEN_SPAWNS)).start()
print "Started Pokemon-spawning module"

if os.path.exists("Despawn.json"):
    with open("Despawn.json", "r") as f:
        despawn_q = json.load(f)
Thread(target=despawn_pokemons, args=(TIME_UNTIL_DESPAWN,)).start()
print "Started Pokemon-despawning module"

print "Server is up"
while True:
    try:
        tcp_server.listen(1)
        conn, (ip, port) = tcp_server.accept()
        new_thread = ClientThread(conn, ip, port)
        new_thread.start()
        threads.append(new_thread)
    except KeyboardInterrupt:
        print "Shutting down server"
        sys.exit()
