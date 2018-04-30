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
from multiprocessing.connection import Listener

from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.support.ui import WebDriverWait

from Player import Player
from Pokemon import Pokemon


class ClientThread(Thread):

    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.player = None
        print "Started thread for %s:%d" % addr

    def run(self):
        self.send_cmd("/login")
        while True:
            data = self.recv_msg()
            try:
                msg = json.loads(data)

                # User login
                if msg["msg"].startswith("/login"):
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
                            self.send_msg("Welcome to PokeServer")
                            self.send_cmd("/choose_game_mode")
                        elif len(players):
                            self.send_msg("Wrong password")
                            self.send_cmd("/login")
                        else:
                            self.send_msg("Username not in use.")
                            self.send_cmd("/register")

                # PokeBat game mode
                elif msg["msg"].startswith("/pokebat"):
                    if len(self.player.pokemons) > 2:
                        self.send_msg("Welcome to PokeBat\n"
                                      "Pick 3 pokemons to participate in PokeBat")
                        self.send_msg(self.pokemon_list(self.player.pokemons))
                        self.send_cmd("/pick")
                        msg = json.loads(self.recv_msg())
                        if not isinstance(msg["msg"], list) and msg["msg"].startswith("/back"):
                            pass
                        else:
                            while any(i < 1 or i > len(self.player.pokemons) for i in msg["msg"]):
                                self.send_msg("Invalid")
                                self.send_cmd("/pick")
                                msg = json.loads(self.recv_msg())
                            with lock:
                                if pokebat_q:
                                    t = pokebat_q.pop(0)
                                    t.connect(self.conn, [self.player.pokemons[i - 1] for i in msg["msg"]])
                                else:
                                    t = PokeCat(self.conn, [self.player.pokemons[i - 1] for i in msg["msg"]])
                                    pokebat_q.append(t)
                                    t.start()
                            t.join()
                            with lock:
                                with open("Info.json", "r+") as f:
                                    players = filter(lambda p: p.username != self.player.username,
                                                     [Player(p) for p in json.load(f)])
                                    players.append(self.player)
                                    f.seek(0)
                                    json.dump([player.serialize() for player in players], f, indent=4,
                                              separators=(",", ": "))
                                    f.truncate()
                    else:
                        self.send_msg("You don't have enough pokemons to play. Catch some more")
                    self.send_cmd("/choose_game_mode")

                # PokeCat game mode
                elif msg["msg"].startswith("/pokecat"):
                    """PokeCat game mode"""
                    self.send_msg("Welcome to PokeCat\n"
                                  "Choose a direction [W/A/S/D] to move\n"
                                  "Enter 'l' or 'list' to see your current pokemons\n"
                                  "Enter 'q' or 'quit' to exit")
                    with lock:
                        self.send_msg(self.map_producer(self.player.pos, world))
                    self.send_cmd("/move")

                # PokeCat movement
                elif msg["msg"].startswith("/move"):
                    direction = msg["msg"][5]
                    row, col = self.player.pos
                    new_row, new_col = row, col
                    with lock:
                        if direction == "W":
                            new_row = max(0, row - 1)
                        elif direction == "S":
                            new_row = min(WORLD_SIZE - 1, row + 1)
                        elif direction == "A":
                            new_col = max(0, col - 1)
                        elif direction == "D":
                            new_col = min(WORLD_SIZE - 1, col + 1)
                        result = self.player.catch(world[new_row][new_col])
                        world[new_row][new_col] = 0
                        self.player.pos = (new_row, new_col)
                        with open("Info.json", "r+") as f:
                            players = filter(lambda p: p.username != self.player.username,
                                             [Player(p) for p in json.load(f)])
                            players.append(self.player)
                            f.seek(0)
                            json.dump([player.serialize() for player in players], f, indent=4,
                                      separators=(",", ": "))
                            f.truncate()
                        self.send_msg(self.map_producer(self.player.pos, world))
                        self.send_msg(result)
                    self.send_cmd("/move")

                # List of Pokemons
                elif msg["msg"].startswith("/list"):
                    self.send_msg(self.pokemon_list(self.player.pokemons))
                    self.send_msg("You can merge 2 Pokemons with the same name using the command 'merge [id] [id]'\n"
                                  "Type 'q' or 'quit' to exit")
                    self.send_cmd("/pokemons")

                # Merge Pokemons
                elif msg["msg"].startswith("/merge"):
                    x, y = map(int, re.findall(r"(\d+) (\d+)", msg["msg"])[0])
                    l = len(self.player.pokemons)
                    if x > l or y > l:
                        self.send_msg("Invalid")
                    elif self.player.pokemons[x-1].name != self.player.pokemons[y-1].name:
                        self.send_msg("Invalid. Incompatible Pokemons")
                    else:
                        self.player.pokemons[x-1].gain_xp(self.player.pokemons[y-1].total_xp())
                        self.player.pokemons.pop(y-1)
                        self.send_msg("Merge successful")
                        self.send_msg(self.pokemon_list(self.player.pokemons))
                    self.send_cmd("/pokemons")

                # User register
                elif msg["msg"].startswith("/register"):
                    cur_player = Player({"username": msg["username"],
                                         "password": msg["password"],
                                         "pos": (randint(0, WORLD_SIZE - 1), randint(0, WORLD_SIZE - 1))})
                    self.register(cur_player)
                    self.player = cur_player
                    self.send_msg("Successfully registered\nWelcome to PokeServer")
                    self.send_cmd("/choose_game_mode")

                # User exit
                elif msg["msg"].startswith("/exit"):
                    print "Client %s:%d disconnected" % self.addr
                    sys.exit()

            except ValueError:
                print "Indecipherable JSON"

    def send_msg(self, msg):
        try:
            self.conn.send(self.format_msg(msg=msg))
        except (socket.error, IOError):
            print "Client %s:%d disconnected" % self.addr
            sys.exit()

    def send_cmd(self, cmd):
        try:
            self.conn.send(self.format_msg(cmd=cmd))
        except (socket.error, IOError):
            print "Client %s:%d disconnected" % self.addr
            sys.exit()

    def recv_msg(self):
        try:
            return self.conn.recv()
        except (IOError, EOFError):
            print "Client %s:%d disconnected" % self.addr
            sys.exit()

    @staticmethod
    def pokemon_list(pokemons):
        li = "Your current pokemons:"
        for i in range(len(pokemons) / 3):
            li += "\n{0}. {1:<20} {2}. {3:<20} {4}. {5:<20}".format(i * 3 + 1, pokemons[i * 3].name + " Lv" + str(
                pokemons[i * 3].level),
                                                                    i * 3 + 2, pokemons[i * 3 + 1].name + " Lv" + str(
                    pokemons[i * 3 + 1].level),
                                                                    i * 3 + 3, pokemons[i * 3 + 2].name + " Lv" + str(
                    pokemons[i * 3 + 2].level))
        if len(pokemons) % 3 == 2:
            li += "\n{0}. {1:<20} {2}. {3:<20}".format(len(pokemons) - 1,
                                                       pokemons[-2].name + " Lv" + str(pokemons[-2].level),
                                                       len(pokemons),
                                                       pokemons[-1].name + " Lv" + str(pokemons[-1].level))
        elif len(pokemons) % 3 == 1:
            li += "\n{0}. {1:<20}".format(len(pokemons), pokemons[-1].name + " Lv" + str(pokemons[-1].level))
        return li

    @staticmethod
    def map_producer((row, col), world):
        padded_world = [[0] * (WORLD_SIZE + MAP_SIZE - 1) for _ in range(MAP_SIZE / 2)] + \
                       map(lambda x: [0] * (MAP_SIZE / 2) + x + [0] * (MAP_SIZE / 2), world) + \
                       [[0] * (WORLD_SIZE + MAP_SIZE - 1) for _ in range(MAP_SIZE / 2)]
        padded_world[row + MAP_SIZE / 2][col + MAP_SIZE / 2] = 1
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


class PokeCat(Thread):

    def __init__(self, p1_conn, p1_pokemons):
        Thread.__init__(self)
        self.p1_conn = p1_conn
        self.p1_pokemons = p1_pokemons
        self.p1_cur_pokemon = p1_pokemons[0]
        self.p2_conn = None
        self.p2_pokemons = None
        self.p2_cur_pokemon = None

    def run(self):
        self.send_msg_p1("Waiting for other player to join...")
        while not self.p2_conn:
            pass
        self.send_msg_p1("Another player has joined. The game is starting")
        self.send_msg_p2("The game is starting")
        if self.p1_cur_pokemon.speed > self.p2_cur_pokemon.speed:
            self.p1_turn()
        elif self.p1_cur_pokemon.speed < self.p2_cur_pokemon.speed:
            self.p2_turn()
        elif randint(1, 2) < 2:
            self.p1_turn()
        else:
            self.p2_turn()

    def p1_turn(self):
        self.send_msg_p1("It is your turn\n"
                         "Your current Pokemon: %s (%d/%d HP)\n"
                         "The opponent's current Pokemon: %s (%d/%d HP)\n"
                         "1. Attack\n"
                         "2. Switch Pokemon\n"
                         "3. Surrender" % (self.p1_cur_pokemon.name, self.p1_cur_pokemon.cur_hp, self.p1_cur_pokemon.max_hp,
                                           self.p2_cur_pokemon.name, self.p2_cur_pokemon.cur_hp, self.p2_cur_pokemon.max_hp))
        self.send_msg_p2("It is the other player's turn")
        self.send_cmd_p1("/action")
        while True:
            data = self.recv_msg_p1()
            try:
                msg = json.loads(data)

                # Attack
                if msg["msg"].startswith("/attack"):
                    if not self.p1_cur_pokemon.is_alive():
                        self.send_msg_p1("Your current pokemon is dead. Please switch pokemon")
                        self.send_cmd_p1("/action")
                    else:
                        if randint(1, 2) < 2:
                            dmg = self.p2_cur_pokemon.take_dmg(self.p1_cur_pokemon.atk)
                        else:
                            dmg = self.p2_cur_pokemon.take_special_dmg(self.p1_cur_pokemon.special_atk,
                                                                       self.p1_cur_pokemon.type)
                        self.send_msg_p1("Your %s hit the opponent's %s for %d damage" % (self.p1_cur_pokemon.name,
                                                                                          self.p2_cur_pokemon.name,
                                                                                          dmg))
                        self.send_msg_p2(
                            "Your %s got hit by the opponent's %s for %d damage" % (self.p2_cur_pokemon.name,
                                                                                    self.p1_cur_pokemon.name,
                                                                                    dmg))
                        if not self.check_winner():
                            self.p2_turn()
                            break

                # Switch
                elif msg["msg"].startswith("/switch"):
                    if self.p1_pokemons[int(msg["msg"][-1]) - 1].is_alive():
                        self.p1_cur_pokemon = self.p1_pokemons[int(msg["msg"][-1]) - 1]
                        self.send_msg_p1("Your current pokemon is %s (%d/%d HP)" % (self.p1_cur_pokemon.name,
                                                                                    self.p1_cur_pokemon.cur_hp,
                                                                                    self.p1_cur_pokemon.max_hp))
                        self.send_msg_p2("The opponent switched Pokemon\n"
                                         "Their current Pokemon is %s (%d/%d HP)" % (self.p1_cur_pokemon.name,
                                                                                     self.p1_cur_pokemon.cur_hp,
                                                                                     self.p1_cur_pokemon.max_hp))
                        if not self.check_winner():
                            self.p2_turn()
                            break
                    else:
                        self.send_msg_p1("That Pokemon is dead. Please choose another Pokemon")
                        self.send_cmd_p1("/action")

                # Surrender
                elif msg["msg"].startswith("/surrender"):
                    self.announce_winner(2)
                    break

            except ValueError:
                print "Indecipherable Json"

    def p2_turn(self):
        self.send_msg_p2("It is your turn\n"
                         "Your current Pokemon: %s (%d/%d HP)\n"
                         "The opponent's current Pokemon: %s (%d/%d HP)\n"
                         "1. Attack\n"
                         "2. Switch Pokemon\n"
                         "3. Surrender" % (self.p2_cur_pokemon.name, self.p2_cur_pokemon.cur_hp, self.p2_cur_pokemon.max_hp,
                                           self.p1_cur_pokemon.name, self.p1_cur_pokemon.cur_hp, self.p1_cur_pokemon.max_hp))
        self.send_msg_p1("It is the other player's turn")
        self.send_cmd_p2("/action")
        while True:
            data = self.recv_msg_p2()
            try:
                msg = json.loads(data)

                # Attack
                if msg["msg"].startswith("/attack"):
                    if not self.p2_cur_pokemon.is_alive():
                        self.send_msg_p2("Your current pokemon is dead. Please switch pokemon")
                        self.send_cmd_p2("/action")
                    else:
                        if randint(1, 2) < 2:
                            dmg = self.p1_cur_pokemon.take_dmg(self.p2_cur_pokemon.atk)
                        else:
                            dmg = self.p1_cur_pokemon.take_special_dmg(self.p2_cur_pokemon.special_atk,
                                                                       self.p2_cur_pokemon.type)
                        self.send_msg_p2("Your %s hit the opponent's %s for %d damage" % (self.p2_cur_pokemon.name,
                                                                                          self.p1_cur_pokemon.name,
                                                                                          dmg))
                        self.send_msg_p1(
                            "Your %s got hit by the opponent's %s for %d damage" % (self.p1_cur_pokemon.name,
                                                                                    self.p2_cur_pokemon.name,
                                                                                    dmg))
                        if not self.check_winner():
                            self.p1_turn()
                            break

                # Switch
                elif msg["msg"].startswith("/switch"):
                    if self.p2_pokemons[int(msg["msg"][-1]) - 1].is_alive():
                        self.p2_cur_pokemon = self.p2_pokemons[int(msg["msg"][-1]) - 1]
                        self.send_msg_p2("Your current Pokemon is %s (%d/%d HP)" % (self.p2_cur_pokemon.name,
                                                                                    self.p2_cur_pokemon.cur_hp,
                                                                                    self.p2_cur_pokemon.max_hp))
                        self.send_msg_p1("The opponent switched Pokemon\n"
                                         "Their current Pokemon is %s (%d/%d HP)" % (self.p2_cur_pokemon.name,
                                                                                     self.p2_cur_pokemon.cur_hp,
                                                                                     self.p2_cur_pokemon.max_hp))
                        if not self.check_winner():
                            self.p1_turn()
                            break
                    else:
                        self.send_msg_p2("That Pokemon is dead. Please choose another Pokemon")
                        self.send_cmd_p2("/action")

                # Surrender
                elif msg["msg"].startswith("/surrender"):
                    self.announce_winner(1)
                    break

            except ValueError:
                print "Indecipherable Json"

    def check_winner(self):
        if all(pokemon.is_alive() is False for pokemon in self.p1_pokemons):
            self.announce_winner(2)
            return True
        elif all(pokemon.is_alive() is False for pokemon in self.p2_pokemons):
            self.announce_winner(1)
            return True
        else:
            return False

    def announce_winner(self, p):
        for p in (self.p2_pokemons + self.p1_pokemons):
            p.cur_hp = p.max_hp
        if p < 2:
            self.send_msg_p1("Congratulation!!! You won the battle")
            self.send_msg_p2("You lost")
            xp = int(round(sum(pokemon.total_xp() for pokemon in self.p2_pokemons) / 3))
            for pokemon in self.p1_pokemons:
                pokemon.gain_xp(xp)
                self.send_msg_p1("Your %s gained %d xp" % (pokemon.name, xp))
        else:
            self.send_msg_p2("Congratulation!!! You won the battle")
            self.send_msg_p1("You lost")
            xp = int(round(sum(pokemon.total_xp() for pokemon in self.p1_pokemons) / 3))
            for pokemon in self.p2_pokemons:
                pokemon.gain_xp(xp)
                self.send_msg_p2("Your %s gained %d xp" % (pokemon.name, xp))

        sys.exit()

    def connect(self, p2_conn, p2_pokemons):
        self.p2_conn = p2_conn
        self.p2_pokemons = p2_pokemons
        self.p2_cur_pokemon = p2_pokemons[0]

    def send_msg_p1(self, msg):
        try:
            self.p1_conn.send(self.format_msg(msg=msg))
        except (socket.error, IOError):
            self.announce_winner(2)

    def send_cmd_p1(self, cmd):
        try:
            self.p1_conn.send(self.format_msg(cmd=cmd))
        except (socket.error, IOError):
            self.announce_winner(2)

    def recv_msg_p1(self):
        try:
            return self.p1_conn.recv()
        except (IOError, EOFError):
            self.announce_winner(2)

    def send_msg_p2(self, msg):
        try:
            self.p2_conn.send(self.format_msg(msg=msg))
        except (socket.error, IOError):
            self.announce_winner(1)

    def send_cmd_p2(self, cmd):
        try:
            self.p2_conn.send(self.format_msg(cmd=cmd))
        except (socket.error, IOError):
            self.announce_winner(1)

    def recv_msg_p2(self):
        try:
            return self.p2_conn.recv()
        except (IOError, EOFError):
            self.announce_winner(1)

    @staticmethod
    def format_msg(cmd="", msg=""):
        return json.dumps({"cmd": cmd,
                           "msg": msg})


#   End of PokeCat Thread


"""Global constants"""
print "Loading server configuration"
try:
    with open("Config.json", "r") as f:
        config = json.load(f)
except IOError:
    print "No configuration file found. Using default configuration"
    config = {"addr": ("", 9999),
              "world": 1000,
              "spawn_num": 50,
              "spawn_time": 60,
              "autosave_time": 600,
              "despawn_time": 300,
              "map": 11}
    with open("Config.json", "w") as f:
        json.dump(config, f, indent=4)
ADDRESS = (config["addr"][0].encode("ascii", "ignore"), config["addr"][1])
WORLD_SIZE = config["world"]
NUMBER_OF_POKEMONS_PER_SPAWN = config["spawn_num"]
TIME_BETWEEN_SPAWNS = config["spawn_time"]
TIME_BETWEEN_AUTOSAVE = config["autosave_time"]
TIME_UNTIL_DESPAWN = config["despawn_time"]
MAP_SIZE = config["map"]

print "Starting server"

"""Global variables"""
tcp_server = Listener(ADDRESS)
pokedex = []
world = []
despawn_q = []
pokebat_q = []
lock = Lock()


def random_points(number_of_points):
    points = []
    global world
    global WORLD_SIZE
    while number_of_points:
        x = randint(0, WORLD_SIZE - 1)
        y = randint(0, WORLD_SIZE - 1)
        if not world[x][y] and (x, y) not in points:
            points.append((x, y))
            number_of_points -= 1
    return points


def spawn_pokemons(number, delay):
    sleep(0.1)
    print "Spawning %d Pokemons every %.2f minutes" % (number, delay / 60.0)
    global world
    global pokedex
    global despawn_q
    while True:
        sleep(delay)
        points = random_points(number)
        despawn_q.append(points)
        with lock:
            for (x, y) in points:
                world[x][y] = Pokemon(pokedex[randint(0, len(pokedex) - 1)].serialize())
            world_copy = world[:]
        with open("World.json", "w") as f:
            json.dump(world_copy, f, indent=4, default=lambda p: p.serialize())
        with open("Despawn.json", "w") as f:
            json.dump(despawn_q, f, indent=4)
        print "Spawned %d Pokemons" % number


def despawn_pokemons(second):
    sleep(0.2)
    print "Despawning Pokemons every %.2f minutes" % (second / 60.0)
    global despawn_q
    global world
    while True:
        if despawn_q:
            sleep(second)
            points = despawn_q.pop(0)
            with lock:
                for (x, y) in points:
                    world[x][y] = 0
                world_copy = world[:]
            with open("World.json", "w") as f:
                json.dump(world_copy, f, indent=4, default=lambda p: p.serialize())
            with open("Despawn.json", "w") as f:
                json.dump(despawn_q, f, indent=4)
            print "Despawned"


def auto_save(second):
    sleep(0.3)
    print "Auto-saving every %.2f minutes" % (second / 60.0)
    while True:
        sleep(second)
        with lock:
            world_copy = world[:]
        while True:
            try:
                move("World.json", "World_backup.json")
                break
            except WindowsError:
                sleep(0.5)
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
                "return document.getElementsByClassName('detail-panel-header')[0].innerHTML").encode("ascii", "ignore")
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
        except (IOError, ValueError):
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
    conn = tcp_server.accept()
    addr = tcp_server.last_accepted
    ClientThread(conn, addr).start()
