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

        self.max_hp = info.get("max_hp") or self.base_hp
        self.cur_hp = info.get("cur_hp") or self.base_hp
        self.atk = info.get("atk") or self.base_atk
        self.defense = info.get("defense") or self.base_def
        self.speed = info.get("speed") or self.base_speed
        self.special_atk = info.get("special_atk") or self.base_special_atk
        self.special_def = info.get("special_def") or self.base_special_def

        self.ev = info.get("ev") or uniform(0.5, 1.0)
        self.accumulated_xp = info.get("accumulated_xp") or 0
        self.level = info.get("level") or 1
        self.required_xp = info.get("required_xp") or self.base_experience

    def total_xp(self):
        return (2**~-self.level-1)*self.base_experience + self.accumulated_xp

    def is_alive(self):
        return self.cur_hp > 0

    def level_up(self):
        self.accumulated_xp -= self.required_xp
        self.required_xp *= 2
        self.max_hp = int(round(self.max_hp*(1+self.ev)))
        self.cur_hp = self.max_hp
        self.atk = int(round(self.atk*(1+self.ev)))
        self.defense = int(round(self.defense*(1+self.ev)))
        self.speed = int(round(self.speed*(1+self.ev)))
        self.special_atk = int(round(self.special_atk*(1+self.ev)))
        self.special_def = int(round(self.special_def*(1+self.ev)))

    def take_dmg(self, dmg):
        self.cur_hp -= dmg - self.defense
        return dmg - self.defense

    def take_special_dmg(self, dmg, types):
        mul = 1.0
        for t in types:
            mul = max([x["multiply"] for x in self.dmg_when_atked if x["type"] == t] + [mul])
        self.cur_hp -= int(round(dmg*mul)) - self.special_def
        return int(round(dmg*mul)) - self.special_def

    def gain_xp(self, xp):
        self.accumulated_xp += xp
        while self.accumulated_xp >= self.required_xp:
            self.level_up()

    def serialize_xp(self):
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
                "dmg_when_atked": self.dmg_when_atked,
                "max_hp": self.max_hp,
                "cur_hp": self.cur_hp,
                "atk": self.atk,
                "defense": self.defense,
                "special_atk": self.special_atk,
                "special_def": self.special_def,
                "ev": self.ev,
                "accumulated_xp": self.accumulated_xp,
                "level": self.level,
                "required_xp": self.required_xp}

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
