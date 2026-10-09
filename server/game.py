"""
game.py  --  THE BRAIN of the game.

It holds the whole world:
  * all the players,
  * all the cities,
  * the clock (which century, which phase, how many seconds left).

The main method is tick(): the server calls it once per second.
"""

# Allow this file to be run on its own too (not only as part of the package).
if __package__ in (None, ""):
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "server"

import random
import time
import uuid

from . import config, bots
from .models import City, Player


class GameWorld:
    def __init__(self):
        self.reset()

    # ============================================================
    #  SET UP A FRESH WORLD
    # ============================================================
    def reset(self):
        self.phase = "voting"          # voting -> playing -> finished
        self.century = None            # decided by the vote
        self.century_index = 0         # 0..4 (which of the 5 centuries we are in)
        self.sub_phase = "build"       # build -> war
        self.time_left = config.BUILD_SECONDS
        self.vote_time_left = config.VOTE_SECONDS
        self.result_century = None
        self.paused = False
        self.difficulty = config.DEFAULT_DIFFICULTY
        self.war_results = []

        self.players: dict[str, Player] = {}
        self.cities: dict[str, City] = {}
        self.votes: dict[str, int] = {}          # player_id -> chosen century
        self.chat: list[dict] = []               # last messages
        self.events: list[dict] = []             # important things that happened
        self.alliances: list[set] = []           # list of groups of player ids
        self.scores: list[dict] = []

        self._create_countries()
        self._create_bots()

        self.system("Welcome! Everyone votes for a starting century.")

    # --- create the cities of every country ---------------------
    def _create_countries(self):
        for country in config.COUNTRIES:
            for i, name in enumerate(country["cities"]):
                cid = f"{country['id']}_{name.lower().replace(' ', '_')}"
                is_cap = (i == 0)
                self.cities[cid] = City(
                    id=cid,
                    name=name,
                    country=country["id"],
                    owner=None,
                    population=config.STARTING_POPULATION if is_cap else random.randint(40, 70),
                    satisfaction=config.BASE_SATISFACTION,
                    defense=config.CITY_BASE_DEFENSE,
                    is_capital=is_cap,
                    x=country["x"],
                    y=country["y"],
                )

    # --- fill the seats with computer players -------------------
    def _create_bots(self):
        names = ["Ada", "Boris", "Cleo", "Dario", "Elena", "Farid", "Gina", "Hugo"]
        # only MAX_PLAYERS countries take part in this game
        chosen = random.sample(config.COUNTRIES, min(config.MAX_PLAYERS, len(config.COUNTRIES)))
        for i, country in enumerate(chosen):
            pid = f"bot_{country['id']}"
            player = Player(
                id=pid,
                name=f"{names[i % len(names)]} (bot)",
                country=country["id"],
                is_bot=True,
                color=country["color"],
                flag=country["flag"],
                money=config.STARTING_MONEY,
                building_points=config.STARTING_BP,
                knowledge_points=config.STARTING_KP,
            )
            self.players[pid] = player
            # give the bot its capital city
            capital = self._capital_of(country["id"])
            capital.owner = pid
            player.cities.append(capital.id)

    def _capital_of(self, country_id: str) -> City:
        for city in self.cities.values():
            if city.country == country_id and city.is_capital:
                return city
        raise ValueError("no capital for " + country_id)

    # ============================================================
    #  PLAYERS JOINING
    # ============================================================
    def join(self, name: str, country_id: str):
        """A human picks a country. If no bot has it, we move a bot there,
        so there are always exactly MAX_PLAYERS players in the game."""
        if self.phase != "voting":
            return None, "The game has already started. Ask to watch instead!"
        country = next((c for c in config.COUNTRIES if c["id"] == country_id), None)
        if country is None:
            return None, "Unknown country."

        # is that country already taken by a human?
        for p in self.players.values():
            if p.country == country_id and not p.is_bot:
                return None, "Sorry, that country is already taken."

        capital = self._capital_of(country_id)

        # if a bot owns it, take over that bot...
        if capital.owner and self.players[capital.owner].is_bot:
            bot = self.players[capital.owner]
        else:
            # ...otherwise move a free bot to this country
            bot = next((p for p in self.players.values() if p.is_bot), None)
            if bot is None:
                return None, "All 8 seats are already taken by humans!"
            for old_id in list(bot.cities):
                self.cities[old_id].owner = None
            bot.cities = []
            capital.owner = bot.id
            bot.cities = [capital.id]
            bot.country = country_id
            bot.color = country["color"]
            bot.flag = country["flag"]

        bot.is_bot = False
        bot.name = name
        # give friends more time to join after someone arrives
        self.vote_time_left = config.VOTE_SECONDS
        self.system(f"{name} joined as {country['name']}!")
        return bot, None

    def get_player(self, player_id: str):
        return self.players.get(player_id)

    def has_human(self) -> bool:
        """Is there at least one real person playing?"""
        return any(not p.is_bot for p in self.players.values())

    def human_count(self) -> int:
        """How many real people are playing?"""
        return sum(1 for p in self.players.values() if not p.is_bot)

    def difficulty_data(self) -> dict:
        return config.DIFFICULTIES.get(self.difficulty, config.DIFFICULTIES["normal"])

    def total_centuries(self) -> int:
        """How many centuries this game lasts (depends on difficulty)."""
        return self.difficulty_data().get("centuries", config.TOTAL_CENTURIES)

    def set_difficulty(self, player_id: str, level: str):
        if self.phase != "voting":
            return "You can only choose the difficulty before the game starts."
        if level not in config.DIFFICULTIES:
            return "Unknown difficulty."
        self.difficulty = level
        d = config.DIFFICULTIES[level]
        self.system(f"{self.players[player_id].name} set difficulty to {d['name']} {d['emoji']}.")
        return None

    def can_pause(self) -> bool:
        """A single player may pause the game (bots do not count)."""
        return self.phase == "playing" and self.human_count() == 1

    def toggle_pause(self, player_id: str):
        if not self.can_pause():
            return "You can only pause when you are the only player."
        self.paused = not self.paused
        self.system("⏸️ The game is paused." if self.paused else "▶️ The game is running again.")
        return None

    # ============================================================
    #  PLAYER ACTIONS
    # ============================================================
    def vote(self, player_id: str, century: int):
        if self.phase != "voting":
            return "Voting is over."
        if century not in config.CENTURY_CHOICES:
            return "You can only vote 10-15 or 20-25."
        self.votes[player_id] = century
        self.system(f"{self.players[player_id].name} voted for century {century}.")
        if len(self.votes) == len(self.players) and self.has_human():
            self._start_game()
        return None

    def build(self, player_id: str, city_id: str, building_id: str):
        p = self.players[player_id]
        city = self.cities.get(city_id)
        if not city or city.owner != player_id:
            return "That is not your city."
        if building_id not in config.BUILDINGS:
            return "Unknown building."
        b = config.BUILDINGS[building_id]
        if p.money < b["cost_money"]:
            return "Not enough money."
        if p.building_points < b["cost_bp"]:
            return "Not enough building points."
        for mat, amount in b.get("materials", {}).items():
            if p.materials.get(mat, 0) < amount:
                return f"Not enough {mat}."
        # pay
        p.money -= b["cost_money"]
        p.building_points -= b["cost_bp"]
        for mat, amount in b.get("materials", {}).items():
            p.materials[mat] -= amount
        # place it
        city.buildings[building_id] = city.buildings.get(building_id, 0) + 1
        city.defense += b.get("defense", 0)
        city.satisfaction = min(100, city.satisfaction + b.get("satisfaction", 0))
        if b.get("war"):
            p.war_points += b["war"]
        return None

    def train(self, player_id: str, troop_id: str, amount: int = 1):
        p = self.players[player_id]
        t = config.TROOPS.get(troop_id)
        if not t:
            return "Unknown troop."
        # need the right building somewhere?
        if t.get("needs") and not self._owns_building(p, t["needs"]):
            return f"You need a {t['needs']} first."
        # need knowledge?
        if t.get("tech") and not p.has_tech(t["tech"]):
            return f"You must unlock {config.TECHS[t['tech']]['name']} first."
        for _ in range(amount):
            if p.money < t["money"] or p.building_points < t["cost_bp"]:
                return "Not enough money or building points."
            if any(p.materials.get(m, 0) < v for m, v in t.get("materials", {}).items()):
                return "Not enough materials."
            p.money -= t["money"]
            p.building_points -= t["cost_bp"]
            for m, v in t.get("materials", {}).items():
                p.materials[m] -= v
            p.troops[troop_id] = p.troops.get(troop_id, 0) + 1
        return None

    def buy(self, player_id: str, material: str, amount: int):
        p = self.players[player_id]
        if material not in config.MATERIALS:
            return "Unknown material."
        price = config.MATERIAL_PRICE[material] * amount
        if p.money < price:
            return "Not enough money."
        p.money -= price
        p.materials[material] = p.materials.get(material, 0) + amount
        return None

    def research(self, player_id: str, tech_id: str):
        p = self.players[player_id]
        t = config.TECHS.get(tech_id)
        if not t:
            return "Unknown knowledge."
        if p.has_tech(tech_id):
            return "You already know that."
        if p.knowledge_points < t["cost_kp"]:
            return "Not enough knowledge points."
        p.knowledge_points -= t["cost_kp"]
        p.techs.append(tech_id)
        self.system(f"{p.name} discovered {t['name']}!")
        return None

    def set_target(self, player_id: str, city_id: str):
        if self.sub_phase != "war":
            return "You can only choose a target during the war phase."
        city = self.cities.get(city_id)
        if not city:
            return "Unknown city."
        if city.owner == player_id:
            return "That is your own city."
        self.players[player_id].target = city_id
        return None

    def say(self, player_id: str, text: str):
        text = (text or "").strip()[:200]
        if not text:
            return
        p = self.players[player_id]
        self.chat.append({"kind": "chat", "name": p.name, "color": p.color, "text": text})
        self.chat = self.chat[-60:]

    def request_alliance(self, player_id: str, other_id: str):
        """Bots may accept. Two allied players will not fight each other."""
        if other_id not in self.players:
            return "Unknown player."
        other = self.players[other_id]
        if other.is_bot:
            if random.random() < 0.7:
                self._make_alliance(player_id, other_id)
                return None
            return f"{other.name} refused your alliance."
        return "Waiting for the other player to accept (coming in a later step)."

    def _make_alliance(self, a: str, b: str):
        for group in self.alliances:
            if a in group or b in group:
                group.add(a)
                group.add(b)
                break
        else:
            self.alliances.append({a, b})
        self.system(f"{self.players[a].name} and {self.players[b].name} are now allies! 🤝")

    def are_allied(self, a: str, b: str) -> bool:
        if a is None or b is None:
            return False
        return any(a in g and b in g for g in self.alliances)

    # ============================================================
    #  THE CLOCK  (called once per second)
    # ============================================================
    def tick(self, dt: float = 1.0):
        # Safety rule: a game with no real players goes back to the lobby,
        # so bots never play alone forever.
        if self.phase != "voting" and not self.has_human():
            self.reset()
            return

        if self.paused:
            return

        if self.phase == "voting":
            # wait for a real person before the vote can count
            if not self.has_human():
                self.vote_time_left = config.VOTE_SECONDS
                return
            self.vote_time_left -= dt
            for p in list(self.players.values()):
                if p.is_bot and p.id not in self.votes:
                    bots.bot_vote(self, p)
            if self.vote_time_left <= 0:
                self._start_game()

        elif self.phase == "playing":
            self.time_left -= dt
            self._run_economy(dt)
            for p in list(self.players.values()):
                if p.is_bot and p.alive and self.sub_phase == "build":
                    bots.bot_act(self, p, dt)

            if self.sub_phase == "build" and self.time_left <= 0:
                self._start_war()
            elif self.sub_phase == "war" and self.time_left <= 0:
                self._resolve_wars()
                self._enter_result()
            elif self.sub_phase == "result" and self.time_left <= 0:
                self._next_century()

    # --- voting is done, begin the game -------------------------
    def _start_game(self):
        if self.phase != "voting":
            return
        if self.votes:
            # the century with the most votes wins (ties -> earliest)
            counts = {}
            for c in self.votes.values():
                counts[c] = counts.get(c, 0) + 1
            self.century = max(sorted(counts), key=lambda c: counts[c])
        else:
            self.century = 12
        self.result_century = self.century
        self.phase = "playing"
        self.century_index = 0

        # give the computer players their difficulty bonus
        d = self.difficulty_data()
        extra = d.get("bot_start_extra", 0)
        if extra:
            for p in self.players.values():
                if p.is_bot:
                    p.money += extra
                    p.building_points += extra / 2
                    for m in config.MATERIALS:
                        p.materials[m] = p.materials.get(m, 0) + 5

        self._enter_build()
        self.system(f"The game begins in the year {self.century}00! Build your civilization. 🏛️")
        self.system(f"Difficulty: {d['name']} {d['emoji']} — {d['info']}")

    def _enter_build(self):
        self.sub_phase = "build"
        self.time_left = config.BUILD_SECONDS
        for p in self.players.values():
            p.target = None

    # --- end of build phase, war begins -------------------------
    def _start_war(self):
        self.sub_phase = "war"
        self.time_left = config.WAR_SECONDS
        self.war_results = []
        self.system(f"⚔️ WAR! Century {self.century} is ending. Choose a city to attack!")
        for p in list(self.players.values()):
            if p.is_bot and p.alive:
                bots.bot_choose_target(self, p)

    # --- war is over; show the results for a few seconds --------
    def _enter_result(self):
        self.sub_phase = "result"
        self.time_left = config.RESULT_SECONDS

    # --- the attack/defense power of a battle -------------------
    def _battle_powers(self, p, city):
        attacker = 10 + p.war_points + self._army_attack(p)
        defender = city.defense
        if city.owner:
            d = self.players[city.owner]
            defender += d.security_points + self._army_defense(d) * config.WAR_DEFENDER_BONUS
        return attacker, defender

    def war_preview(self):
        """The battles people have chosen, with attack/defense power."""
        rows = []
        if self.sub_phase != "war":
            return rows
        for p in self.players.values():
            if not p.alive or not p.target:
                continue
            city = self.cities.get(p.target)
            if not city or city.owner == p.id:
                continue
            attack, defense = self._battle_powers(p, city)
            defender = city.owner
            rows.append({
                "attacker": p.id, "attacker_name": p.name, "attacker_color": p.color,
                "city": city.id, "city_name": city.name,
                "defender": defender,
                "defender_name": self.players[defender].name if defender else "Neutral",
                "attack": round(attack), "defense": round(defense),
            })
        return rows

    # --- fight every battle -------------------------------------
    def _resolve_wars(self):
        self.war_results = []
        for p in list(self.players.values()):
            if not p.alive or not p.target:
                continue
            city = self.cities.get(p.target)
            if not city or city.owner == p.id:
                continue
            defender_id = city.owner
            attack, defense = self._battle_powers(p, city)
            captured = attack * random.uniform(0.85, 1.15) > defense * random.uniform(0.85, 1.15)

            if captured:
                self._capture(p, city)
            else:
                self.system(f"{p.name} attacked {city.name} but was pushed back. 🛡️")

            self.war_results.append({
                "attacker": p.id, "attacker_name": p.name, "attacker_color": p.color,
                "city": city.id, "city_name": city.name,
                "defender": defender_id,
                "defender_name": self.players[defender_id].name if defender_id else "Neutral",
                "attack": round(attack), "defense": round(defense),
                "captured": captured,
            })
        # clear targets for next time
        for p in self.players.values():
            p.target = None

    def _capture(self, winner: Player, city: City):
        old_owner_id = city.owner
        stay = max(5, city.population // 2)
        flee = city.population - stay
        city.population = stay
        city.owner = winner.id
        if city.id not in winner.cities:
            winner.cities.append(city.id)

        if old_owner_id:
            loser = self.players[old_owner_id]
            if city.id in loser.cities:
                loser.cities.remove(city.id)
            self._spread_refugees(loser, flee)
            self.system(f"🔥 {winner.name} captured {city.name} from {loser.name}! ({stay} people stayed, {flee} fled)")
            if not loser.cities:
                loser.alive = False
                self.system(f"💀 {loser.name} lost their last city and is out of the game!")
        else:
            self.system(f"🏳️ {winner.name} captured the neutral city of {city.name}! ({stay} people stayed)")

    def _spread_refugees(self, loser: Player, amount: int):
        if amount <= 0 or not loser.cities:
            return
        each = max(1, amount // len(loser.cities))
        for cid in loser.cities:
            c = self.cities[cid]
            c.population += each
            c.satisfaction = max(10, c.satisfaction - 3)   # war makes people sad

    # --- move on to the next century ----------------------------
    def _next_century(self):
        self.century_index += 1
        if self.century_index >= self.total_centuries():
            self._finish_game()
            return
        self.century += 1
        self._enter_build()
        self.system(f"🏛️ Welcome to century {self.century}00. Build again!")

    def _finish_game(self):
        self.phase = "finished"
        self.scores = self.compute_scores()
        if self.scores:
            winner = self.scores[0]
            self.system(f"🏆 {winner['name']} wins the game with {winner['score']} city points!")

    # ============================================================
    #  ECONOMY  (money, points, materials, happiness)
    # ============================================================
    def _run_economy(self, dt: float):
        bot_mult = self.difficulty_data()["bot_economy"]
        for p in self.players.values():
            if not p.alive:
                continue
            cities = [self.cities[cid] for cid in p.cities]
            population = sum(c.population for c in cities)
            happiness = self._avg_satisfaction(cities) / 100.0
            m = bot_mult if p.is_bot else 1.0

            tax_mult = 1.5 if p.has_tech("banking") else 1.0
            p.money += population * config.TAX_PER_CITIZEN * happiness * tax_mult * dt * m

            bp_bonus = 0.0
            money_bonus = 0.0
            for c in cities:
                for bid, count in c.buildings.items():
                    bp_bonus += config.BUILDINGS[bid].get("building_bonus", 0) * count
                    money_bonus += config.BUILDINGS[bid].get("money_bonus", 0) * count
            p.building_points += (config.BP_PER_SECOND + bp_bonus) * dt * m
            p.money += money_bonus * happiness * dt * m
            p.knowledge_points += config.KP_PER_SECOND * dt * m

            # people grow when they are happy and there is room
            for c in cities:
                cap = config.STARTING_POPULATION + sum(
                    config.BUILDINGS[b].get("capacity", 0) * n for b, n in c.buildings.items()
                )
                if c.satisfaction > 50 and c.population < cap * 8:
                    c.population += config.POP_GROWTH * (c.satisfaction / 100.0) * dt

            # if there is no war, people slowly cheer up
            if self.sub_phase == "build":
                for c in cities:
                    c.satisfaction = min(100, c.satisfaction + 0.02 * dt)

            # a little security and war points trickle from your stuff
            p.security_points = sum(c.defense for c in cities)
            p.war_points = max(p.war_points, sum(
                config.BUILDINGS[b].get("war", 0) * n for c in cities for b, n in c.buildings.items()
            ))

    def _avg_satisfaction(self, cities) -> float:
        if not cities:
            return 0.0
        return sum(c.satisfaction for c in cities) / len(cities)

    def _owns_building(self, p: Player, building_id: str) -> bool:
        return any(
            building_id in self.cities[cid].buildings for cid in p.cities
        )

    def _army_attack(self, p: Player) -> float:
        total = 0.0
        for tid, n in p.troops.items():
            total += config.TROOPS[tid]["attack"] * n
        return total

    def _army_defense(self, p: Player) -> float:
        total = 0.0
        for tid, n in p.troops.items():
            total += config.TROOPS[tid]["defense"] * n
        return total

    # ============================================================
    #  SCORES
    # ============================================================
    def compute_scores(self) -> list[dict]:
        rows = []
        for p in self.players.values():
            citizens = sum(self.cities[cid].population for cid in p.cities)
            buildings = sum(self.cities[cid].building_points_value() for cid in p.cities)
            resources = sum(p.materials.values()) + p.troops_total_value() + p.money / 20.0
            score = citizens + buildings + resources
            rows.append({
                "id": p.id,
                "name": p.name,
                "country": p.country,
                "flag": p.flag,
                "alive": p.alive,
                "citizens": round(citizens),
                "buildings": round(buildings),
                "resources": round(resources),
                "score": round(score),
                "cities": len(p.cities),
            })
        rows.sort(key=lambda r: r["score"], reverse=True)
        return rows

    # ============================================================
    #  TEXT LOG
    # ============================================================
    def system(self, text: str):
        self.events.append({"kind": "event", "text": text, "t": time.time()})
        self.events = self.events[-40:]

    # ============================================================
    #  SAVE / LOAD
    # ============================================================
    def snapshot(self) -> dict:
        """Everything we need to write to the save file."""
        return {
            "phase": self.phase,
            "century": self.century,
            "century_index": self.century_index,
            "sub_phase": self.sub_phase,
            "time_left": self.time_left,
            "vote_time_left": self.vote_time_left,
            "result_century": self.result_century,
            "paused": self.paused,
            "difficulty": self.difficulty,
            "war_results": self.war_results,
            "players": {pid: p.__dict__ for pid, p in self.players.items()},
            "cities": {cid: c.__dict__ for cid, c in self.cities.items()},
            "votes": self.votes,
            "chat": self.chat,
            "events": self.events,
            "alliances": [sorted(g) for g in self.alliances],
            "scores": self.scores,
        }

    def restore(self, data: dict):
        """Rebuild the world from the save file."""
        self.phase = data["phase"]
        self.century = data["century"]
        self.century_index = data["century_index"]
        self.sub_phase = data["sub_phase"]
        self.time_left = data["time_left"]
        self.vote_time_left = data["vote_time_left"]
        self.result_century = data.get("result_century")
        self.paused = data.get("paused", False)
        self.difficulty = data.get("difficulty", config.DEFAULT_DIFFICULTY)
        self.war_results = data.get("war_results", [])
        self.players = {}
        for pid, raw in data["players"].items():
            p = Player(id=raw["id"], name=raw["name"], country=raw["country"])
            p.__dict__.update(raw)
            self.players[pid] = p
        self.cities = {}
        for cid, raw in data["cities"].items():
            c = City(id=raw["id"], name=raw["name"], country=raw["country"],
                     owner=raw["owner"], population=raw["population"])
            c.__dict__.update(raw)
            self.cities[cid] = c
        self.votes = data["votes"]
        self.chat = data["chat"]
        self.events = data["events"]
        self.alliances = [set(g) for g in data["alliances"]]
        self.scores = data.get("scores", [])

    # ============================================================
    #  WHAT THE BROWSER SEES
    # ============================================================
    def public_state(self, viewer_id: str | None = None) -> dict:
        return {
            "phase": self.phase,
            "century": self.century,
            "century_index": self.century_index,
            "total_centuries": self.total_centuries(),
            "sub_phase": self.sub_phase,
            "time_left": round(self.time_left, 1),
            "vote_time_left": round(self.vote_time_left, 1),
            "paused": self.paused,
            "human_count": self.human_count(),
            "can_pause": self.can_pause(),
            "can_reset": self.human_count() <= 1,
            "difficulty": self.difficulty,
            "difficulties": config.DIFFICULTIES,
            "war_preview": self.war_preview(),
            "war_results": self.war_results,
            "century_choices": config.CENTURY_CHOICES,
            "players": {pid: p.to_dict() for pid, p in self.players.items()},
            "cities": {cid: c.to_dict() for cid, c in self.cities.items()},
            "votes": self.votes,
            "chat": self.chat,
            "events": self.events,
            "alliances": [sorted(g) for g in self.alliances],
            "scores": self.scores,
            "viewer": viewer_id,
            "countries": config.COUNTRIES,
            "buildings": config.BUILDINGS,
            "troops": config.TROOPS,
            "techs": config.TECHS,
            "materials": config.MATERIALS,
            "material_price": config.MATERIAL_PRICE,
        }
