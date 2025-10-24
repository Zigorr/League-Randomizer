import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Riot API Configuration
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

# Riot API Endpoints
RIOT_API_BASE = "https://{region}.api.riotgames.com"
RIOT_ACCOUNT_API = "https://americas.api.riotgames.com"
DATA_DRAGON_BASE = "https://ddragon.leagueoflegends.com"

# Supported regions for Riot API
REGIONS = {
    'na1': 'americas',
    'br1': 'americas',
    'la1': 'americas',
    'la2': 'americas',
    'euw1': 'europe',
    'eun1': 'europe',
    'tr1': 'europe',
    'ru': 'europe',
    'kr': 'asia',
    'jp1': 'asia',
    'oc1': 'sea',
    'ph2': 'sea',
    'sg2': 'sea',
    'th2': 'sea',
    'tw2': 'sea',
    'vn2': 'sea',
}

# File paths
DATA_DIR = "data"
ASSETS_DIR = "assets"
PLAYERS_FILE = f"{DATA_DIR}/league_players.json"
CHAMPION_ROLES_FILE = f"{DATA_DIR}/champion_roles.json"
CHAMPION_CACHE_FILE = f"{DATA_DIR}/champion_cache.json"
SUMMONERS_RIFT_IMAGE = f"{ASSETS_DIR}/summoners_rift.jpg"

# Game mode configuration
GAME_MODES = {
    6: {
        'name': '3v3',
        'roles': ['Top', 'Mid', 'Bot']
    },
    8: {
        'name': '4v4',
        'roles': ['Top', 'Mid', 'Bot'],  # + random Jungle/Support
        'random_role': ['Jungle', 'Support']
    },
    10: {
        'name': '5v5',
        'roles': ['Top', 'Jungle', 'Mid', 'Bot', 'Support']
    }
}

# Map coordinates for champion placement on Summoner's Rift
# Based on standard 512x512 map dimensions (will be scaled appropriately)
ROLE_POSITIONS = {
    'Top': (130, 120),      # Top lane area
    'Jungle': (220, 240),   # Jungle between top and mid
    'Mid': (256, 256),      # Center of the map
    'Bot': (380, 390),      # Bot lane area
    'Support': (350, 420)   # Near bot lane, slightly offset
}

