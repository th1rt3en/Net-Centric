class Player:
    """Player Object"""

    def __init__(self, info):
        self.username = info["username"]
        self.password = info["password"]
        self.pokemons = []

    def catch(self, pokemon):
        if len(self.pokemons) < 200:
            self.pokemons.append(pokemon)

    def serialize_with_pokemon(self):
        return {"username": self.username,
                "password": self.password,
                "pokemons": [pokemon.serialize() for pokemon in self.pokemons]}

    def serialize(self):
        return {"username": self.username,
                "password": self.password}
