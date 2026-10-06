"""
storage.py  --  saving and loading the world.

We write one file:  data/save.json
So if you stop the server and start it again, the game comes back.
"""

# Allow this file to be run on its own too (not only as part of the package).
if __package__ in (None, ""):
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "server"

import json
import os

from .game import GameWorld

DATA_DIR = os.environ.get("GCARDS_DATA", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))
SAVE_PATH = os.path.join(DATA_DIR, "save.json")


def save(world: GameWorld):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(world.snapshot(), f, ensure_ascii=False, indent=1)


def load_or_new() -> GameWorld:
    """Load the saved world, or make a brand new one."""
    world = GameWorld()
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            world.restore(data)
            print("Loaded saved game from", SAVE_PATH)
        except Exception as e:
            print("Could not read save file, starting fresh.", e)
    return world
