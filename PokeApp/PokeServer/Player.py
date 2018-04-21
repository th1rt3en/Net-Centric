class Player:
    """Player Object"""

    def __init__(self, info):
        self.__username = info["username"]
        self.__password = info["password"]

    def serialize(self):
        return {"username": self.__username,
                "password": self.__password}

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @username.setter
    def username(self, username):
        self.__username = username

    @password.setter
    def password(self, password):
        self.__password = password