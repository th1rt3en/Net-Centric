class Pokemon:
    """Pokemon Object"""

    def __init__(self, info):
        self.__id = info["id"]
        self.__name = info["name"]
        self.__hp = info["hp"]
        self.__atk = info["atk"]
        self.__dfs = info["dfs"]
        self.__spd = info["spd"]
        self.__sp_atk = info["sp_atk"]
        self.__sp_dfs = info["sp_dfs"]

    def serialize(self):
        return {"id": self.__id,
                "name": self.__name,
                "hp": self.__hp,
                "atk": self.__atk,
                "dfs": self.__dfs,
                "spd": self.__spd,
                "sp_atk": self.__sp_atk,
                "sp_dfs": self.__sp_dfs}

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def hp(self):
        return self.__hp

    @property
    def atk(self):
        return self.__atk

    @property
    def spd(self):
        return self.__spd

    @property
    def dfs(self):
        return self.__dfs

    @property
    def sp_atk(self):
        return self.__sp_atk

    @property
    def sp_dfs(self):
        return self.__sp_dfs

    @id.setter
    def id(self, id):
        self.id = id

    @name.setter
    def name(self, name):
        self.name = name

    @hp.setter
    def hp(self, hp):
        self.hp = hp

    @atk.setter
    def atk(self, atk):
        self.atk = atk

    @dfs.setter
    def dfs(self, dfs):
        self.dfs = dfs

    @spd.setter
    def spd(self, spd):
        self.spd = spd

    @sp_atk.setter
    def sp_atk(self, sp_atk):
        self.sp_atk = sp_atk

    @sp_dfs.setter
    def sp_dfs(self, sp_dfs):
        self.sp_dfs = sp_dfs

