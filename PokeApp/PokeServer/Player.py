from Pokemon import Pokemon


class Player:
    """Player Object"""

    def __init__(self, info):
        self.username = info["username"]
        self.password = info["password"]
        self.pos = info.get("pos")
        if info.get("pokemons"):
            self.pokemons = [Pokemon(pokemon) for pokemon in info.get("pokemons")]
        else:
            self.pokemons = []

    def catch(self, pokemon):
        if isinstance(pokemon, Pokemon):
            if len(self.pokemons) < 200:
                self.pokemons.append(pokemon)
                return "You just caught a %s" % pokemon.name
            else:
                return "Failed to catch %s. Maximum capacity reached" % pokemon.name
        else:
            return "There's nothing here"

    def serialize(self):
        return {"username": self.username,
                "password": self.password,
                "pokemons": [pokemon.serialize_xp() for pokemon in self.pokemons],
                "pos": self.pos}
