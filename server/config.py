"""
config.py  --  THE GAME RULEBOOK

Every important number of the game lives here.
Want the game to be faster, cheaper, or stronger? Just change a number
below and restart the server. Nothing else needs to change.
"""

import os


def _load_dotenv():
    """Read KEY=VALUE lines from the .env file in the project folder."""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

# Password needed to click "Start a new game" (set in the .env file).
RESET_PASSWORD = os.environ.get("GCARDS_RESET_PASSWORD", "")

# ---------------------------------------------------------------
#  TIME
# ---------------------------------------------------------------
SECONDS_PER_CENTURY = 300      # one century = 5 minutes (300 seconds)
BUILD_SECONDS = int(os.environ.get("GCARDS_BUILD_SECONDS", "240"))  # 4 minutes of building
WAR_SECONDS = int(os.environ.get("GCARDS_WAR_SECONDS", "60"))       # 1 minute of war
RESULT_SECONDS = 6             # a short pause to show the battle results
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
VOTE_SECONDS = 180             # how long players may gather in the lobby (3 minutes)
CENTURY_CHOICES = list(range(10, 16)) + list(range(20, 26))  # 10..15 and 20..25

# ---------------------------------------------------------------
#  COUNTRIES  (~50 major countries; each has 3 cities)
#  lat/lon is the capital's location (used to place it on the map).
#  Only MAX_PLAYERS of them are real players each game; the rest are neutral.
# ---------------------------------------------------------------
_RAW_COUNTRIES = [
    # id, name, flag, capital lat, capital lon, [3 cities]
    # --- Europe ---
    ("england", "England", "🇬🇧", 51.51, -0.13, ["London", "Manchester", "Birmingham"]),
    ("france", "France", "🇫🇷", 48.86, 2.35, ["Paris", "Marseille", "Lyon"]),
    ("germany", "Germany", "🇩🇪", 52.52, 13.40, ["Berlin", "Munich", "Hamburg"]),
    ("italy", "Italy", "🇮🇹", 41.90, 12.50, ["Rome", "Milan", "Naples"]),
    ("spain", "Spain", "🇪🇸", 40.42, -3.70, ["Madrid", "Barcelona", "Seville"]),
    ("portugal", "Portugal", "🇵🇹", 38.72, -9.14, ["Lisbon", "Porto", "Faro"]),
    ("netherlands", "Netherlands", "🇳🇱", 52.37, 4.90, ["Amsterdam", "Rotterdam", "The Hague"]),
    ("belgium", "Belgium", "🇧🇪", 50.85, 4.35, ["Brussels", "Antwerp", "Ghent"]),
    ("poland", "Poland", "🇵🇱", 52.23, 21.01, ["Warsaw", "Krakow", "Gdansk"]),
    ("sweden", "Sweden", "🇸🇪", 59.33, 18.07, ["Stockholm", "Gothenburg", "Malmo"]),
    ("norway", "Norway", "🇳🇴", 59.91, 10.75, ["Oslo", "Bergen", "Trondheim"]),
    ("denmark", "Denmark", "🇩🇰", 55.68, 12.57, ["Copenhagen", "Aarhus", "Odense"]),
    ("finland", "Finland", "🇫🇮", 60.17, 24.94, ["Helsinki", "Tampere", "Turku"]),
    ("greece", "Greece", "🇬🇷", 37.98, 23.73, ["Athens", "Thessaloniki", "Patras"]),
    ("ukraine", "Ukraine", "🇺🇦", 50.45, 30.52, ["Kyiv", "Kharkiv", "Odesa"]),
    ("croatia", "Croatia", "🇭🇷", 45.81, 15.98, ["Zagreb", "Split", "Dubrovnik"]),
    ("romania", "Romania", "🇷🇴", 44.43, 26.10, ["Bucharest", "Cluj", "Timisoara"]),
    ("switzerland", "Switzerland", "🇨🇭", 47.38, 8.54, ["Zurich", "Geneva", "Basel"]),
    ("ireland", "Ireland", "🇮🇪", 53.35, -6.26, ["Dublin", "Cork", "Galway"]),
    # --- Asia ---
    ("turkey", "Turkey", "🇹🇷", 39.93, 32.86, ["Ankara", "Istanbul", "Izmir"]),
    ("russia", "Russia", "🇷🇺", 55.75, 37.62, ["Moscow", "St Petersburg", "Novosibirsk"]),
    ("china", "China", "🇨🇳", 39.90, 116.40, ["Beijing", "Shanghai", "Guangzhou"]),
    ("japan", "Japan", "🇯🇵", 35.68, 139.69, ["Tokyo", "Osaka", "Kyoto"]),
    ("india", "India", "🇮🇳", 28.61, 77.21, ["Delhi", "Mumbai", "Bangalore"]),
    ("southkorea", "South Korea", "🇰🇷", 37.57, 126.98, ["Seoul", "Busan", "Incheon"]),
    ("indonesia", "Indonesia", "🇮🇩", -6.21, 106.85, ["Jakarta", "Surabaya", "Bandung"]),
    ("vietnam", "Vietnam", "🇻🇳", 21.03, 105.85, ["Hanoi", "Ho Chi Minh City", "Da Nang"]),
    ("thailand", "Thailand", "🇹🇭", 13.76, 100.50, ["Bangkok", "Chiang Mai", "Phuket"]),
    ("philippines", "Philippines", "🇵🇭", 14.60, 120.98, ["Manila", "Cebu", "Davao"]),
    ("pakistan", "Pakistan", "🇵🇰", 33.68, 73.05, ["Islamabad", "Karachi", "Lahore"]),
    ("iran", "Iran", "🇮🇷", 35.69, 51.39, ["Tehran", "Mashhad", "Isfahan"]),
    ("saudiarabia", "Saudi Arabia", "🇸🇦", 24.71, 46.68, ["Riyadh", "Jeddah", "Mecca"]),
    ("kazakhstan", "Kazakhstan", "🇰🇿", 51.17, 71.45, ["Astana", "Almaty", "Shymkent"]),
    ("israel", "Israel", "🇮🇱", 31.78, 35.22, ["Jerusalem", "Tel Aviv", "Haifa"]),
    # --- Africa ---
    ("egypt", "Egypt", "🇪🇬", 30.04, 31.24, ["Cairo", "Alexandria", "Giza"]),
    ("morocco", "Morocco", "🇲🇦", 34.02, -6.84, ["Rabat", "Casablanca", "Marrakesh"]),
    ("nigeria", "Nigeria", "🇳🇬", 9.06, 7.49, ["Abuja", "Lagos", "Kano"]),
    ("southafrica", "South Africa", "🇿🇦", -25.75, 28.19, ["Pretoria", "Cape Town", "Johannesburg"]),
    ("kenya", "Kenya", "🇰🇪", -1.29, 36.82, ["Nairobi", "Mombasa", "Kisumu"]),
    ("ethiopia", "Ethiopia", "🇪🇹", 9.03, 38.74, ["Addis Ababa", "Dire Dawa", "Mekelle"]),
    ("algeria", "Algeria", "🇩🇿", 36.75, 3.06, ["Algiers", "Oran", "Constantine"]),
    ("ghana", "Ghana", "🇬🇭", 5.60, -0.19, ["Accra", "Kumasi", "Tamale"]),
    ("tanzania", "Tanzania", "🇹🇿", -6.16, 35.75, ["Dodoma", "Dar es Salaam", "Mwanza"]),
    # --- Americas ---
    ("usa", "USA", "🇺🇸", 38.90, -77.04, ["Washington", "New York", "Los Angeles"]),
    ("canada", "Canada", "🇨🇦", 45.42, -75.70, ["Ottawa", "Toronto", "Vancouver"]),
    ("mexico", "Mexico", "🇲🇽", 19.43, -99.13, ["Mexico City", "Guadalajara", "Monterrey"]),
    ("brazil", "Brazil", "🇧🇷", -15.79, -47.88, ["Brasilia", "Sao Paulo", "Rio de Janeiro"]),
    ("argentina", "Argentina", "🇦🇷", -34.60, -58.38, ["Buenos Aires", "Cordoba", "Rosario"]),
    ("colombia", "Colombia", "🇨🇴", 4.71, -74.07, ["Bogota", "Medellin", "Cali"]),
    ("peru", "Peru", "🇵🇪", -12.05, -77.04, ["Lima", "Arequipa", "Cusco"]),
    ("chile", "Chile", "🇨🇱", -33.45, -70.67, ["Santiago", "Valparaiso", "Concepcion"]),
    # --- Oceania ---
    ("australia", "Australia", "🇦🇺", -35.28, 149.13, ["Canberra", "Sydney", "Melbourne"]),
    ("newzealand", "New Zealand", "🇳🇿", -41.29, 174.78, ["Wellington", "Auckland", "Christchurch"]),
]


def _map_x(lon):
    """Longitude -> x position (%) on the world map image."""
    return 0.002733 * lon + 0.4828


def _map_y(lat):
    """Latitude -> y position (%) on the world map image."""
    return -0.005647 * lat + 0.5528


def _country_color(index):
    hue = (index * 137.508) % 360
    return f"hsl({hue:.0f}, 68%, 55%)"


COUNTRIES = [
    {
        "id": cid,
        "name": name,
        "flag": flag,
        "color": _country_color(i),
        "capital": cities[0],
        "lat": lat,
        "lon": lon,
        "x": round(_map_x(lon) * 100, 2),
        "y": round(_map_y(lat) * 100, 2),
        "cities": cities,
    }
    for i, (cid, name, flag, lat, lon, cities) in enumerate(_RAW_COUNTRIES)
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
        "info": "Short game (3 centuries). Computer players are slow and friendly.",
        "centuries": 3,
        "bot_activity": 0.30,
        "bot_economy": 0.8,
        "bot_start_extra": 0,
        "bot_attacks": 0.5,
    },
    "normal": {
        "name": "Normal", "emoji": "😐",
        "info": "5 centuries. A fair fight.",
        "centuries": 5,
        "bot_activity": 0.50,
        "bot_economy": 1.0,
        "bot_start_extra": 0,
        "bot_attacks": 0.85,
    },
    "hard": {
        "name": "Hard", "emoji": "😈",
        "info": "Long game (7 centuries). Computer players are rich, quick and ruthless.",
        "centuries": 7,
        "bot_activity": 0.85,
        "bot_economy": 1.5,
        "bot_start_extra": 250,
        "bot_attacks": 1.0,
    },
}
