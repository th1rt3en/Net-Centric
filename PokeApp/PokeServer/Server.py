import requests
import os
import re
import json
import urllib2
from bs4 import BeautifulSoup
from Pokemon import Pokemon
from contextlib import closing
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait


class Server:
    """PokeApp Server"""

    def __init__(self):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)

    def start(self):
        print "Starting", self.__doc__
        self.update_pokedex()

    def update_pokedex(self):
        print "Checking Pokedex version"
        if not os.path.exists("pokedex.json"):
            print "Pokedex not found"
            self.init_pokedex()

    def init_pokedex(self):
        print "Getting Pokedex"
        pokemons = []
        with closing(Chrome("chromedriver.exe")) as browser:
            browser.get("https://www.pokedex.org/")
            number_of_pokemons = browser.execute_script("return document.getElementById('monsters-list').getElementsByTagName('li').length")
            print "Found %d Pokemons" % number_of_pokemons
            print "Downloading info..."
            for id in range(1, number_of_pokemons + 1):
                browser.get("https://www.pokedex.org/#/pokemon/" + str(id))
                WebDriverWait(browser, 2).until(lambda x: x.execute_script("return document.getElementsByClassName('detail-national-id')[0].children[0].innerHTML")[1:] == str(id))
                name =  browser.execute_script("return document.getElementsByClassName('detail-panel-header')[0].innerHTML")
                hp = browser.execute_script("return document.getElementsByClassName('stat-bar')[0].children[1].innerHTML")
                atk = browser.execute_script("return document.getElementsByClassName('stat-bar')[1].children[1].innerHTML")
                dfs = browser.execute_script("return document.getElementsByClassName('stat-bar')[2].children[1].innerHTML")
                spd = browser.execute_script("return document.getElementsByClassName('stat-bar')[3].children[1].innerHTML")
                sp_atk = browser.execute_script("return document.getElementsByClassName('stat-bar')[4].children[1].innerHTML")
                sp_dfs = browser.execute_script("return document.getElementsByClassName('stat-bar')[5].children[1].innerHTML")
                pokemon = Pokemon(id, name, hp, atk, dfs, spd, sp_atk, sp_dfs)
                pokemons.append(pokemon)
                print "Downloaded %d/%d Pokemons" % (id, number_of_pokemons)


s = Server()
s.start()
