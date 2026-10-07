"""
bots.py  --  the computer players.

They are not very smart yet, but they keep the game alive and fun.
Each bot: votes, builds, buys, trains soldiers, and picks a target.
"""

# Allow this file to be run on its own too (not only as part of the package).
if __package__ in (None, ""):
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "server"

import random

from . import config


def bot_vote(world, player):
    choices = list(config.CENTURY_CHOICES)
    world.vote(player.id, random.choice(choices))


def bot_act(world, player, dt):
    """Called about once per second during the build phase."""
    d = config.DIFFICULTIES.get(world.difficulty, config.DIFFICULTIES["normal"])
    # how often a bot acts depends on the difficulty
    if random.random() > d["bot_activity"]:
        return

    cities = [world.cities[cid] for cid in player.cities]
    if not cities:
        return

    # 1) always try to keep people happy with houses / temples
    avg_happy = sum(c.satisfaction for c in cities) / len(cities)
    city = random.choice(cities)

    if avg_happy < 65 and _try_build(world, player, city, "temple"):
        return
    if _try_build(world, player, city, "house"):
        return

    # 2) make sure there is a barracks and a wall
    if not world._owns_building(player, "barracks"):
        if _try_build(world, player, city, "barracks"):
            return
    if _try_build(world, player, city, "wall"):
        return

    # 3) buy some materials so we can build later
    if random.random() < 0.4:
        mat = random.choice(config.MATERIALS)
        world.buy(player.id, mat, random.randint(1, 3))

    # 4) train some troops
    for tid in ["soldier", "samurai", "ninja", "witch"]:
        t = config.TROOPS.get(tid, {})
        if t.get("tech") and not player.has_tech(t["tech"]):
            continue
        world.train(player.id, tid, 1)
        break

    # 5) study sometimes
    if player.knowledge_points > 40:
        locked = [k for k in config.TECHS if not player.has_tech(k)]
        if locked:
            world.research(player.id, random.choice(locked))


def _try_build(world, player, city, building_id) -> bool:
    before = city.buildings.get(building_id, 0)
    err = world.build(player.id, city.id, building_id)
    if err is None and city.buildings.get(building_id, 0) > before:
        return True
    return False


def bot_choose_target(world, player):
    """Pick the easiest enemy city to attack."""
    d = config.DIFFICULTIES.get(world.difficulty, config.DIFFICULTIES["normal"])
    if random.random() > d["bot_attacks"]:
        return
    best = None
    best_def = 99999
    for city in world.cities.values():
        if city.owner == player.id:
            continue
        if city.owner and world.are_allied(player.id, city.owner):
            continue
        if city.defense < best_def:
            best = city
            best_def = city.defense
    if best:
        player.target = best.id
