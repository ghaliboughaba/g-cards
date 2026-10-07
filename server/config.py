"""
config.py  --  THE GAME RULEBOOK

Every important number of the game lives here.
Want the game to be faster, cheaper, or stronger? Just change a number
below and restart the server. Nothing else needs to change.
"""

# ---------------------------------------------------------------
#  TIME
# ---------------------------------------------------------------
SECONDS_PER_CENTURY = 300      # one century = 5 minutes (300 seconds)
BUILD_SECONDS = 240            # 4 minutes of building at the start of a century
WAR_SECONDS = 60               # 1 minute of war at the end of a century
TOTAL_CENTURIES = 5            # a whole game lasts 5 centuries
TICK = 1.0                     # the game thinks once per second

# ---------------------------------------------------------------
#  STARTING VALUES (what every player begins with)
# ---------------------------------------------------------------
STARTING_POPULATION = 100      # you start with 100 citizens
STARTING_MONEY = 300
STARTING_BP = 40               # building points
STARTING_KP = 0                # knowledge points
BASE_SATISFACTION = 70         # citizens start fairly happy (0..100)
CITY_BASE_DEFENSE = 10         # a city defends itself a little

# ---------------------------------------------------------------
#  VOTING
# ---------------------------------------------------------------
MAX_PLAYERS = 8                # one seat per country (see COUNTRIES below)
VOTE_SECONDS = 90              # how long players may vote before it auto-starts
CENTURY_CHOICES = list(range(10, 16)) + list(range(20, 26))  # 10..15 and 20..25

# ---------------------------------------------------------------
#  COUNTRIES  (small countries only, as requested)
# ---------------------------------------------------------------
COUNTRIES = [
    {"id": "croatia", "name": "Croatia", "flag": "🇭🇷", "capital": "Zagreb",     "color": "#e63946"},
    {"id": "morocco", "name": "Morocco", "flag": "🇲🇦", "capital": "Rabat",      "color": "#2a9d8f"},
    {"id": "italy",   "name": "Italy",   "flag": "🇮🇹", "capital": "Rome",       "color": "#457b9d"},
    {"id": "japan",   "name": "Japan",   "flag": "🇯🇵", "capital": "Tokyo",      "color": "#e76f51"},
    {"id": "denmark", "name": "Denmark", "flag": "🇩🇰", "capital": "Copenhagen", "color": "#8e7dbe"},
    {"id": "usa",     "name": "USA",     "flag": "🇺🇸", "capital": "Washington", "color": "#2563eb", "bot_only": True},
    {"id": "france",  "name": "France",  "flag": "🇫🇷", "capital": "Paris",      "color": "#7c3aed", "bot_only": True},
    {"id": "england", "name": "England", "flag": "🇬🇧", "capital": "London",     "color": "#b91c1c", "bot_only": True},
]

# ---------------------------------------------------------------
#  RAW MATERIALS
# ---------------------------------------------------------------
MATERIALS = ["iron", "stone", "gold", "diamond"]

MATERIAL_EMOJI = {
    "iron": "⛓️",
    "stone": "🪨",
    "gold": "🪙",
    "diamond": "💎",
}

MATERIAL_PRICE = {          # how much it costs to BUY 1 unit
    "iron": 4,
    "stone": 2,
    "gold": 12,
    "diamond": 30,
}

# ---------------------------------------------------------------
#  BUILDINGS  (built inside a city)
# ---------------------------------------------------------------
BUILDINGS = {
    "house": {
        "name": "House", "emoji": "🏠",
        "cost_money": 60, "materials": {"stone": 10}, "cost_bp": 4,
        "satisfaction": 4, "capacity": 25, "points": 5,
        "info": "More room for people. +4 happiness, +25 people limit.",
    },
    "farm": {
        "name": "Farm", "emoji": "🌾",
        "cost_money": 40, "materials": {"stone": 5}, "cost_bp": 3,
        "satisfaction": 2, "capacity": 10, "points": 4,
        "info": "Feeds people. +2 happiness, people grow faster.",
    },
    "market": {
        "name": "Market", "emoji": "🏪",
        "cost_money": 80, "materials": {"stone": 15}, "cost_bp": 6,
        "satisfaction": 3, "money_bonus": 0.5, "points": 8,
        "info": "Trades goods. +3 happiness, +money each second.",
    },
    "temple": {
        "name": "Temple", "emoji": "⛩️",
        "cost_money": 100, "materials": {"stone": 20, "gold": 5}, "cost_bp": 8,
        "satisfaction": 8, "points": 10,
        "info": "People feel calm. +8 happiness.",
    },
    "wall": {
        "name": "Wall", "emoji": "🧱",
        "cost_money": 70, "materials": {"stone": 25}, "cost_bp": 6,
        "defense": 15, "points": 6,
        "info": "Protects the city. +15 security points in war.",
    },
    "barracks": {
        "name": "Barracks", "emoji": "⚔️",
        "cost_money": 90, "materials": {"iron": 20, "stone": 10}, "cost_bp": 7,
        "war": 10, "points": 7, "unlocks": ["soldier"],
        "info": "Trains soldiers. +10 war points.",
    },
    "workshop": {
        "name": "Workshop", "emoji": "🔨",
        "cost_money": 120, "materials": {"iron": 25}, "cost_bp": 10,
        "building_bonus": 1.0, "points": 12,
        "info": "Makes building points faster. +1 building point each second.",
    },
}

# ---------------------------------------------------------------
#  TROOPS  (you train them; "needs" = building required)
# ---------------------------------------------------------------
TROOPS = {
    "soldier": {
        "name": "Soldier", "emoji": "🪖",
        "attack": 6, "defense": 5,
        "money": 25, "materials": {"iron": 5}, "cost_bp": 2,
        "needs": "barracks",
    },
    "samurai": {
        "name": "Samurai", "emoji": "🥋",
        "attack": 14, "defense": 9,
        "money": 60, "materials": {"iron": 12, "gold": 2}, "cost_bp": 5,
        "needs": "barracks", "tech": "steel_weapons",
    },
    "ninja": {
        "name": "Ninja", "emoji": "🥷",
        "attack": 16, "defense": 4,
        "money": 70, "materials": {"iron": 8}, "cost_bp": 5,
        "needs": "barracks", "tech": "stealth",
    },
    "spy": {
        "name": "Spy", "emoji": "🕵️",
        "attack": 3, "defense": 3,
        "money": 80, "materials": {"gold": 5}, "cost_bp": 4,
        "needs": "barracks", "tech": "stealth", "special": "steal",
        "info": "Steals money and resources from an enemy.",
    },
    "witch": {
        "name": "Witch", "emoji": "🧙",
        "attack": 20, "defense": 10,
        "money": 150, "materials": {"gold": 10, "diamond": 2}, "cost_bp": 10,
        "needs": "temple", "tech": "magic",
        "info": "Magic weakens the enemy before battle.",
    },
    "armored_car": {
        "name": "Armored Car", "emoji": "🚙",
        "attack": 30, "defense": 20,
        "money": 220, "materials": {"iron": 30, "gold": 5}, "cost_bp": 15,
        "needs": "workshop", "tech": "armored_car",
    },
}

# ---------------------------------------------------------------
#  KNOWLEDGE  (spend knowledge points to unlock new things)
# ---------------------------------------------------------------
TECHS = {
    "masonry":       {"name": "Masonry",       "emoji": "🧱", "cost_kp": 20, "info": "Stronger walls (+10 security per wall)."},
    "stealth":       {"name": "Stealth",       "emoji": "🥷", "cost_kp": 40, "info": "Unlock Ninja and Spy."},
    "steel_weapons": {"name": "Steel Weapons", "emoji": "🗡️", "cost_kp": 40, "info": "Unlock Samurai."},
    "magic":         {"name": "Magic",         "emoji": "✨", "cost_kp": 70, "info": "Unlock Witch."},
    "armored_car":   {"name": "Armored Cars",  "emoji": "🚙", "cost_kp": 90, "info": "Unlock Armored Car."},
    "banking":       {"name": "Banking",       "emoji": "💰", "cost_kp": 50, "info": "+50% money from taxes."},
}

# ---------------------------------------------------------------
#  ECONOMY RATES  (how fast things appear each second)
# ---------------------------------------------------------------
TAX_PER_CITIZEN = 0.03         # money per citizen per second (x happiness)
BP_PER_SECOND = 0.5            # building points every second
KP_PER_SECOND = 0.15           # knowledge points every second
POP_GROWTH = 0.12              # new citizens per second (when happy + room)
WAR_DEFENDER_BONUS = 1.15      # defenders are a little stronger (small advantage)

# ---------------------------------------------------------------
#  DIFFICULTY  (how strong the computer players are)
#    bot_activity    = how often a bot does something (0..1)
#    bot_economy     = multiplier on bot money / building points / knowledge
#    bot_start_extra = extra money bots get when the game begins
#    bot_attacks     = chance a bot attacks in a war (0..1)
# ---------------------------------------------------------------
DEFAULT_DIFFICULTY = "normal"

DIFFICULTIES = {
    "easy": {
        "name": "Easy", "emoji": "🙂",
        "info": "Computer players are slow and friendly.",
        "bot_activity": 0.30,
        "bot_economy": 0.8,
        "bot_start_extra": 0,
        "bot_attacks": 0.5,
    },
    "normal": {
        "name": "Normal", "emoji": "😐",
        "info": "A fair fight.",
        "bot_activity": 0.50,
        "bot_economy": 1.0,
        "bot_start_extra": 0,
        "bot_attacks": 0.85,
    },
    "hard": {
        "name": "Hard", "emoji": "😈",
        "info": "Computer players are rich, quick and ruthless.",
        "bot_activity": 0.85,
        "bot_economy": 1.5,
        "bot_start_extra": 250,
        "bot_attacks": 1.0,
    },
}
