import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

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

