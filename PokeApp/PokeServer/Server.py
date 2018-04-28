import json
import os
import re
import socket
import sys
from contextlib import closing
from random import randint
from threading import Thread, Lock
from time import sleep
from shutil import move

from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.support.ui import WebDriverWait

from Player import Player
from Pokemon import Pokemon


class ClientThread(Thread):

    def __init__(self, conn, ip, port):
        Thread.__init__(self)
        self.conn = conn
        self.ip = ip
        self.port = port
        self.player = None
        print "Started thread for %s:%d" % (ip, port)

    def run(self):
        self.conn.send(self.format_msg(cmd="/login"))
        while True:
            try:
                data = self.conn.recv(1024)
            except socket.error:
                print "Client %s:%d disconnected" % (self.ip, self.port)
                sys.exit()
            try:
                msg = json.loads(data)
                if msg["msg"].startswith("/login"):
                    """User login"""
                    cur_player = Player({"username": msg["username"], "password": msg["password"]})
                    if not os.path.exists("Info.json"):
                        open("Info.json", "w").close()
                    with open("Info.json", "r") as f:
                        try:
                            players = [Player(player) for player in json.load(f)]
                        except ValueError:
                            players = []
                        players = filter(lambda p: p.username == cur_player.username, players)
                        if len(players) and players[0].password == cur_player.password:
                            self.player = players[0]
                            self.conn.send(self.format_msg(msg="Welcome to PokeServer"))
                            self.conn.send(self.format_msg(cmd="/choose_game_mode"))
                        elif len(players):
                            self.conn.send(self.format_msg(msg="Wrong password"))
                            self.conn.send(self.format_msg(cmd="/login"))
                        else:
                            self.conn.send(self.format_msg(msg="Username not in use."))
                            self.conn.send(self.format_msg(cmd="/register"))

                elif msg["msg"].startswith("/pokebat"):
                    """PokeBat game mode"""
                    self.conn.send(self.format_msg(msg="Not Available"))
                    self.conn.send(self.format_msg(cmd="/choose_game_mode"))

                elif msg["msg"].startswith("/pokecat"):
                    """PokeCat game mode"""
                    global world
                    self.conn.send(self.format_msg(msg="Welcome to PokeCat"))
                    with lock:
                        self.conn.send(self.format_msg(msg=self.map_producer(self.player.pos, world)))
                    sleep(0.1)
                    self.conn.send(self.format_msg(cmd="/move"))

                elif msg["msg"].startswith("/move"):
                    """PokeCat movement"""
                    global world
                    direction = msg["msg"][5]
                    row, col = self.player.pos
                    new_row, new_col = row, col
                    with lock:
                        if direction == "W":
                            new_row = max(0, row-1)
                        elif direction == "S":
                            new_row = min(WORLD_SIZE-1, row+1)
                        elif direction == "A":
                            new_col = max(0, col-1)
                        elif direction == "D":
                            new_col = min(WORLD_SIZE-1, col+1)
                        self.conn.send(self.format_msg(msg=self.player.catch(world[new_row][new_col])))
                        world[new_row][new_col] = 0
                        self.player.pos = (new_row, new_col)
                        with open("Info.json", "r+") as f:
                            players = filter(lambda p: p.username != self.player.username, [Player(p) for p in json.load(f)])
                            players.append(self.player)
                            f.seek(0)
                            json.dump([player.serialize() for player in players], f, indent=4,
                                      separators=(",", ": "))
                            f.truncate()
                        self.conn.send(self.format_msg(msg=self.map_producer(self.player.pos, world)))
                    sleep(0.1)
                    self.conn.send(self.format_msg(cmd="/move"))

                elif msg["msg"].startswith("/register"):
                    """User register"""
                    cur_player = Player({"username": msg["username"],
                                         "password": msg["password"],
                                         "pos": (randint(0, WORLD_SIZE-1), randint(0, WORLD_SIZE-1))})
                    self.register(cur_player)
                    self.player = cur_player
                    self.conn.send(self.format_msg(msg="Successfully registered\nWelcome to PokeServer"))
                    self.conn.send(self.format_msg(cmd="/choose_game_mode"))

                elif msg["msg"].startswith("/exit"):
                    """User exit"""
                    print "Client %s:%d disconnected" % (self.ip, self.port)
                    self.conn.close()
                    sys.exit()

            except ValueError:
                print "Indecipherable JSON"

    @staticmethod
    def map_producer((row, col), world):
        padded_world = [[0] * (WORLD_SIZE+MAP_SIZE-1) for _ in range(MAP_SIZE/2)] + \
                       map(lambda x: [0]*(MAP_SIZE/2) + x + [0]*(MAP_SIZE/2), world) + \
                       [[0] * (WORLD_SIZE+MAP_SIZE-1) for _ in range(MAP_SIZE/2)]
        padded_world[row+MAP_SIZE/2][col+MAP_SIZE/2] = 1
        m = [r[col:col + MAP_SIZE] for r in padded_world[row:row + MAP_SIZE]]
        return "You are at (%d:%d)\n" % (row, col) + "\n".join(
            ["".join(map(lambda x: "O " if x == 1 else "X " if x else "_ ", r)) for r in m])

    @staticmethod
    def register(player):
        with open("Info.json", "r+") as f:
            try:
                players = [Player(p) for p in json.load(f)]
            except ValueError:
                players = []
            players.append(player)
            f.seek(0)
            json.dump([player.serialize() for player in players], f, indent=4,
                      separators=(",", ": "))
            f.truncate()

    @staticmethod
    def format_msg(cmd="", msg=""):
        return json.dumps({"cmd": cmd,
                           "msg": msg})


#   End of ClientThread


"""Global constants"""
TCP_IP = ""
TCP_PORT = 9997
BUFFER_SIZE = 1024
WORLD_SIZE = 1000
NUMBER_OF_POKEMONS_PER_SPAWN = 200
TIME_BETWEEN_SPAWNS = 10
TIME_BETWEEN_AUTOSAVE = 600
TIME_UNTIL_DESPAWN = 300
MAP_SIZE = 15

print "Starting server"

"""Global variables"""
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind((TCP_IP, TCP_PORT))
threads = []
pokedex = []
world = []
despawn_q = []
lock = Lock()


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
    print "Spawning %d Pokemons every %.2f minutes" % (number, delay/60.0)
    global world
    global pokedex
    global despawn_q
    while True:
        sleep(delay)
        points = random_points(number)
        despawn_q.append(points)
        with lock:
            for (x, y) in points:
                world[x][y] = Pokemon(pokedex[randint(0, len(pokedex)-1)].serialize())
        with open("World.json", "w") as f:
            json.dump(world, f, indent=4, default=lambda p: p.serialize())
        with open("Despawn.json", "w") as f:
            json.dump(despawn_q, f, indent=4)
        print "Spawned %d Pokemons" % number


def despawn_pokemons(second):
    sleep(0.2)
    print "Despawning Pokemons every %.2f minutes" % (second/60.0)
    global despawn_q
    global world
    while True:
        if despawn_q:
            sleep(second)
            points = despawn_q.pop(0)
            with lock:
                for (x, y) in points:
                    world[x][y] = 0
            with open("World.json", "w") as f:
                json.dump(world, f, indent=4, default=lambda p: p.serialize())
            with open("Despawn.json", "w") as f:
                json.dump(despawn_q, f, indent=4)
            print "Despawned"


def auto_save(second):
    sleep(0.3)
    print "Auto-saving every %.2f minutes" % (second/60.0)
    while True:
        sleep(second)
        with lock:
            world_copy = world[:]
        move("World.json", "World_backup.json")
        with open("World.json", "w") as f:
            json.dump(world_copy, f, indent=4, default=lambda p: p.serialize())


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
            pokedex[id - 1].base_experience = int(browser.execute_script(
                "return document.getElementsByTagName('tbody')[0].children[%d].children[3].innerHTML" % i).strip())
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
    try:
        with open("World.json", "r") as f:
            world = [[Pokemon(item) if item else item for item in line] for line in json.load(f)]
    except ValueError:
        print "World.json is corrupted. Loading from backup."
        try:
            with open("World_backup.json") as f:
                world = [[Pokemon(item) if item else item for item in line] for line in json.load(f)]
        except IOError:
            print "No backup found. Creating new PokeWorld"
            world = [[0] * WORLD_SIZE for _ in range(WORLD_SIZE)]
            with open("World.json", "w") as f:
                json.dump(world, f, indent=4)
print "Done loading PokeWorld"

Thread(target=spawn_pokemons, args=(NUMBER_OF_POKEMONS_PER_SPAWN, TIME_BETWEEN_SPAWNS)).start()
print "Started Pokemon-spawning module"

if os.path.exists("Despawn.json"):
    with open("Despawn.json", "r") as f:
        despawn_q = json.load(f)
Thread(target=despawn_pokemons, args=(TIME_UNTIL_DESPAWN,)).start()
print "Started Pokemon-despawning module"

Thread(target=auto_save, args=(TIME_BETWEEN_AUTOSAVE,)).start()
print "Started auto-saving module"

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
