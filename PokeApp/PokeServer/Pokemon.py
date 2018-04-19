class Pokemon:
    """Pokemon Object"""

    def __init__(self, id, name, hp, atk, dfs, spd, sp_atk, sp_dfs):
        self.__id = id
        self.__name = name
        self.__hp = hp
        self.__atk = atk
        self.__dfs = dfs
        self.__spd = spd
        self.__sp_atk = sp_atk
        self.__sp_dfs = sp_dfs

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
    def dfs(self):
        return self.__dfs

    @property
    def sp_atk(self):
        return self.__sp_atk

    @property
    def sp_dfs(self):
        return self.__sp_dfs

