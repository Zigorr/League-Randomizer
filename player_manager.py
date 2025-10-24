import json
import os
from config import PLAYERS_FILE, DATA_DIR

class PlayerManager:
    def __init__(self):
        self.players = {}
        self.load_players()
    
    def load_players(self):
        """Load players from JSON file"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        if os.path.exists(PLAYERS_FILE):
            try:
                with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
                    self.players = json.load(f)
            except Exception as e:
                print(f"Error loading players: {e}")
                self.players = {}
        else:
            self.players = {}
    
    def save_players(self):
        """Save players to JSON file"""
        try:
            with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.players, f, indent=2)
        except Exception as e:
            print(f"Error saving players: {e}")
    
    def register_player(self, discord_id, discord_name):
        """Register a player"""
        discord_id = str(discord_id)
        
        if discord_id in self.players:
            return False, "Player already registered"
        
        self.players[discord_id] = {
            'discord_name': discord_name
        }
        
        self.save_players()
        return True, f"Registered {discord_name}"
    
    def unregister_player(self, discord_id):
        """Unregister a player"""
        discord_id = str(discord_id)
        
        if discord_id not in self.players:
            return False, "Player not registered"
        
        discord_name = self.players[discord_id]['discord_name']
        del self.players[discord_id]
        self.save_players()
        
        return True, f"Unregistered {discord_name}"
    
    def is_registered(self, discord_id):
        """Check if a player is registered"""
        return str(discord_id) in self.players
    
    def get_player(self, discord_id):
        """Get player data"""
        return self.players.get(str(discord_id))
    
    def get_all_players(self):
        """Get all registered players"""
        return self.players
    
    def get_registered_players_in_list(self, discord_ids):
        """Get registered players from a list of Discord IDs"""
        registered = []
        for discord_id in discord_ids:
            if self.is_registered(discord_id):
                registered.append({
                    'discord_id': str(discord_id),
                    **self.players[str(discord_id)]
                })
        return registered
    

# Global instance
player_manager = PlayerManager()

