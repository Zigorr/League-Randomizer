import aiohttp
import json
import os
from config import (
    RIOT_API_KEY, 
    RIOT_API_BASE, 
    RIOT_ACCOUNT_API, 
    DATA_DRAGON_BASE,
    CHAMPION_CACHE_FILE,
    REGIONS
)

class RiotAPI:
    def __init__(self):
        self.api_key = RIOT_API_KEY
        self.session = None
        
    async def init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_latest_version(self):
        """Get latest League of Legends version from Data Dragon"""
        await self.init_session()
        try:
            async with self.session.get(f"{DATA_DRAGON_BASE}/api/versions.json") as response:
                if response.status == 200:
                    versions = await response.json()
                    return versions[0]  # Latest version
        except Exception as e:
            print(f"Error fetching latest version: {e}")
        return None
    
    async def get_all_champions(self):
        """Get all champions from Data Dragon and cache them"""
        await self.init_session()
        
        # Check cache first
        if os.path.exists(CHAMPION_CACHE_FILE):
            with open(CHAMPION_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                if cache.get('version'):
                    return cache
        
        # Fetch from Data Dragon
        version = await self.get_latest_version()
        if not version:
            return {'version': '', 'champions': {}}
        
        try:
            url = f"{DATA_DRAGON_BASE}/cdn/{version}/data/en_US/champion.json"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    champions = {}
                    
                    # Process champion data
                    for champ_id, champ_data in data['data'].items():
                        champions[champ_id] = {
                            'id': champ_data['id'],
                            'key': champ_data['key'],
                            'name': champ_data['name'],
                            'title': champ_data['title'],
                            'image': f"{DATA_DRAGON_BASE}/cdn/{version}/img/champion/{champ_data['id']}.png"
                        }
                    
                    # Cache the data
                    cache_data = {
                        'version': version,
                        'champions': champions
                    }
                    
                    with open(CHAMPION_CACHE_FILE, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, indent=2)
                    
                    return cache_data
        except Exception as e:
            print(f"Error fetching champions: {e}")
        
        return {'version': '', 'champions': {}}
    
    async def get_champion_image_url(self, champion_id):
        """Get champion portrait URL"""
        cache = await self.get_all_champions()
        if champion_id in cache['champions']:
            return cache['champions'][champion_id]['image']
        return None
    
    async def get_puuid(self, game_name, tag_line, region='na1'):
        """Convert Riot ID (gameName#tagLine) to PUUID"""
        await self.init_session()
        
        if not self.api_key:
            print("No Riot API key provided")
            return None
        
        # Get routing value based on region
        routing = REGIONS.get(region.lower(), 'americas')
        
        try:
            url = f"https://{routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
            headers = {'X-Riot-Token': self.api_key}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['puuid']
                elif response.status == 404:
                    print(f"Riot account not found: {game_name}#{tag_line}")
                elif response.status == 403:
                    print("Invalid Riot API key")
                else:
                    print(f"Error fetching PUUID: {response.status}")
        except Exception as e:
            print(f"Error getting PUUID: {e}")
        
        return None
    
    async def get_champion_mastery(self, puuid, region='na1'):
        """Get all champion masteries for a player"""
        await self.init_session()
        
        if not self.api_key:
            print("No Riot API key provided")
            return []
        
        try:
            url = f"{RIOT_API_BASE.format(region=region)}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
            headers = {'X-Riot-Token': self.api_key}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    masteries = await response.json()
                    # Extract champion IDs (as strings to match cache keys)
                    champion_ids = [str(mastery['championId']) for mastery in masteries]
                    return champion_ids
                elif response.status == 404:
                    print(f"Summoner not found with PUUID: {puuid}")
                else:
                    print(f"Error fetching champion mastery: {response.status}")
        except Exception as e:
            print(f"Error getting champion mastery: {e}")
        
        return []
    
    async def get_owned_champions(self, game_name, tag_line, region='na1'):
        """Get list of champion IDs owned by a player"""
        puuid = await self.get_puuid(game_name, tag_line, region)
        if not puuid:
            return []
        
        champion_ids = await self.get_champion_mastery(puuid, region)
        
        # Convert champion IDs (numeric) to champion names
        cache = await self.get_all_champions()
        owned_champions = []
        
        for champ_id, champ_data in cache['champions'].items():
            if champ_data['key'] in champion_ids:
                owned_champions.append(champ_id)
        
        return owned_champions
    
    async def download_image(self, url):
        """Download an image from URL and return bytes"""
        await self.init_session()
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.read()
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")
        return None

# Global instance
riot_api = RiotAPI()

