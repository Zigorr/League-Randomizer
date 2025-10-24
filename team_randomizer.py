import random
from config import GAME_MODES

class TeamRandomizer:
    def __init__(self):
        pass
    
    def is_valid_player_count(self, count):
        """Check if player count is valid (6, 8, or 10)"""
        return count in GAME_MODES
    
    def get_game_mode(self, player_count):
        """Get game mode configuration based on player count"""
        return GAME_MODES.get(player_count)
    
    def create_teams(self, players):
        """
        Create two balanced teams from a list of players
        
        Args:
            players: List of player dicts with discord_id and other info
        
        Returns:
            tuple: (team1, team2, game_mode_info)
        """
        player_count = len(players)
        
        if not self.is_valid_player_count(player_count):
            return None, None, None
        
        game_mode = self.get_game_mode(player_count)
        
        # Shuffle and split players
        shuffled_players = players.copy()
        random.shuffle(shuffled_players)
        
        team_size = player_count // 2
        team1 = shuffled_players[:team_size]
        team2 = shuffled_players[team_size:]
        
        return team1, team2, game_mode
    
    def assign_roles(self, team, game_mode):
        """
        Assign roles to a team
        
        Args:
            team: List of players
            game_mode: Game mode configuration dict
        
        Returns:
            list: Team with roles assigned [{player_data, 'role': role_name}, ...]
        """
        roles = game_mode['roles'].copy()
        
        # Handle 4v4 mode - randomly add Jungle or Support
        if 'random_role' in game_mode:
            random_role = random.choice(game_mode['random_role'])
            roles.append(random_role)
        
        # Shuffle roles
        random.shuffle(roles)
        
        # Assign roles to players
        team_with_roles = []
        for i, player in enumerate(team):
            player_copy = player.copy()
            player_copy['role'] = roles[i]
            team_with_roles.append(player_copy)
        
        return team_with_roles
    
    def randomize_teams(self, players):
        """
        Complete randomization: create teams and assign roles
        
        Args:
            players: List of registered player dicts
        
        Returns:
            dict: {
                'team1': [...],
                'team2': [...],
                'game_mode': {...},
                'random_role': 'Jungle' or 'Support' (for 4v4 only)
            }
        """
        team1, team2, game_mode = self.create_teams(players)
        
        if not team1:
            return None
        
        # Assign roles
        team1_with_roles = self.assign_roles(team1, game_mode)
        team2_with_roles = self.assign_roles(team2, game_mode)
        
        result = {
            'team1': team1_with_roles,
            'team2': team2_with_roles,
            'game_mode': game_mode,
            'random_role': None
        }
        
        # Track which role was selected for 4v4
        if 'random_role' in game_mode:
            # Both teams will have the same 4 roles
            team1_roles = set(p['role'] for p in team1_with_roles)
            for possible_role in game_mode['random_role']:
                if possible_role in team1_roles:
                    result['random_role'] = possible_role
                    break
        
        return result

# Global instance
team_randomizer = TeamRandomizer()

