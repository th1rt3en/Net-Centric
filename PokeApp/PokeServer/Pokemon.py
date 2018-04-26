from random import uniform

class Pokemon:
    """Pokemon Object"""

    def __init__(self, info):
        self.id = info["id"]
        self.name = info["name"]
        self.type = info["type"]
        self.base_experience = info.get("base_experience", 0)
        self.base_hp = info["base_hp"]
        self.base_atk = info["base_atk"]
        self.base_def = info["base_def"]
        self.base_speed = info["base_speed"]
        self.base_special_atk = info["base_special_atk"]
        self.base_special_def = info["base_special_def"]
        self.dmg_when_atked = info["dmg_when_atked"]

        self.max_hp = self.base_hp
        self.cur_hp = self.base_hp
        self.atk = self.base_atk
        self.defense = self.base_def
        self.speed = self.base_speed
        self.special_atk = self.base_special_atk
        self.special_def = self.base_special_def

        self.ev = uniform(0.5, 1.0)
        self.accumulated_xp = 0
        self.level = 1
        self.required_xp = self.base_experience

    def total_xp(self):
        return (2**~-self.level-1)*self.base_experience + self.accumulated_xp

    def level_up(self):
        self.accumulated_xp = 0
        self.required_xp *= 2
        self.max_hp *= 1 + self.ev
        self.cur_hp = self.max_hp
        self.atk *= 1 + self.ev
        self.defense *= 1 + self.ev
        self.speed *= 1 + self.ev
        self.special_atk *= 1 + self.ev
        self.special_def *= 1 + self.ev

    def take_dmg(self, dmg):
        self.cur_hp -= dmg - self.defense
        return self.cur_hp <= 0

    def take_special_dmg(self, dmg, types):
        mul = 1
        for type in types:
            mul = max(max(x["multiply"] for x in self.dmg_when_atked if x["type"] == type), mul)
        self.cur_hp -= dmg*mul - self.special_def
        return self.cur_hp <= 0

    def gain_xp(self, xp):
        self.accumulated_xp += xp
        if self.accumulated_xp >= self.required_xp:
            self.levelup()

    def serialize(self):
        return {"id": self.id,
                "name": self.name,
                "type": self.type,
                "base_experience": self.base_experience,
                "base_hp": self.base_hp,
                "base_atk": self.base_atk,
                "base_def": self.base_def,
                "base_speed": self.base_speed,
                "base_special_atk": self.base_special_atk,
                "base_special_def": self.base_special_def,
                "dmg_when_atked": self.dmg_when_atked}
