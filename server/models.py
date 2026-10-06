"""
models.py  --  the SHAPES of the things in the game.

A "City" and a "Player" are simple boxes that hold numbers.
to_dict() turns the box into text so the browser can read it.
"""

# Allow this file to be run on its own too (not only as part of the package).
if __package__ in (None, ""):
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "server"

from dataclasses import dataclass, field


@dataclass
class City:
    id: str
    name: str
    country: str              # which country it is in (e.g. "japan")
    owner: str | None         # player id, or None if nobody owns it
    population: int
    satisfaction: float = 70.0
    buildings: dict = field(default_factory=dict)   # building_id -> how many
    defense: int = 10
    is_capital: bool = False
    x: int = 0                # position on the map (for later)
    y: int = 0

    def building_points_value(self) -> int:
        """How many points the buildings in this city are worth."""
        from . import config
        total = 0
        for bid, count in self.buildings.items():
            total += config.BUILDINGS[bid]["points"] * count
        return total

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "owner": self.owner,
            "population": round(self.population),
            "satisfaction": round(self.satisfaction, 1),
            "buildings": self.buildings,
            "defense": self.defense,
            "is_capital": self.is_capital,
            "x": self.x,
            "y": self.y,
        }


@dataclass
class Player:
    id: str
    name: str
    country: str
    is_bot: bool = False
    color: str = "#888888"
    flag: str = "🏳️"

    # money and points
    money: float = 300.0
    building_points: float = 40.0
    knowledge_points: float = 0.0
    war_points: float = 0.0
    security_points: float = 0.0

    # raw materials
    materials: dict = field(default_factory=lambda: {"iron": 0, "stone": 0, "gold": 0, "diamond": 0})

    # army
    troops: dict = field(default_factory=dict)      # troop_id -> how many

    # unlocked knowledge
    techs: list = field(default_factory=list)

    # owned cities
    cities: list = field(default_factory=list)      # list of city ids

    alive: bool = True
    target: str | None = None                        # city chosen to attack this century

    def has_tech(self, tech: str) -> bool:
        return tech in self.techs

    def total_troops(self) -> int:
        return sum(self.troops.values())

    def troops_total_value(self) -> int:
        """Rough point value of the whole army (used for the final score)."""
        from . import config
        total = 0
        for tid, n in self.troops.items():
            t = config.TROOPS.get(tid, {})
            total += (t.get("attack", 0) + t.get("defense", 0)) * n
        return total

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "country": self.country,
            "is_bot": self.is_bot,
            "color": self.color,
            "flag": self.flag,
            "money": round(self.money),
            "building_points": round(self.building_points),
            "knowledge_points": round(self.knowledge_points),
            "war_points": round(self.war_points),
            "security_points": round(self.security_points),
            "materials": {k: round(v) for k, v in self.materials.items()},
            "troops": self.troops,
            "techs": self.techs,
            "cities": self.cities,
            "alive": self.alive,
            "target": self.target,
        }
