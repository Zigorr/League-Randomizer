import random
import json
from config import CHAMPION_ROLES_FILE

class ChampionRandomizer:
    def __init__(self):
        self.champion_roles = {}
        self.load_champion_roles()
    
    def load_champion_roles(self):
        """Load champion roles from JSON file"""
        try:
            with open(CHAMPION_ROLES_FILE, 'r', encoding='utf-8') as f:
                self.champion_roles = json.load(f)
        except Exception as e:
            print(f"Error loading champion roles: {e}")
            self.champion_roles = {}
    
    def get_champions_for_role(self, role):
        """Get all champions that can play a specific role"""
        champions = []
        for champion, roles in self.champion_roles.items():
            if role in roles:
                champions.append(champion)
        return champions
    
    def get_owned_champions_for_role(self, owned_champions, role):
        """Get owned champions that can play a specific role"""
        if not owned_champions:
            # If no owned champions, return all champions for the role
            return self.get_champions_for_role(role)
        
        valid_champions = []
        for champion in owned_champions:
            if champion in self.champion_roles:
                if role in self.champion_roles[champion]:
                    valid_champions.append(champion)
        
        return valid_champions
    
    def get_roles_for_champion(self, champion):
        """Get all roles a champion can play"""
        return self.champion_roles.get(champion, [])
    
    def can_swap_roles(self, player1, player2, used_champions):
        """
        Check if two players can swap roles based on their champion pools
        
        Args:
            player1: Player dict with 'role' and 'owned_champions'
            player2: Player dict with 'role' and 'owned_champions'
            used_champions: Set of already used champion names
        
        Returns:
            bool: True if swap is possible
        """
        # Get available champions for swapped roles
        p1_champs_for_p2_role = self.get_owned_champions_for_role(
            player1.get('owned_champions', []), 
            player2['role']
        )
        p2_champs_for_p1_role = self.get_owned_champions_for_role(
            player2.get('owned_champions', []), 
            player1['role']
        )
        
        # Filter out used champions
        p1_available = [c for c in p1_champs_for_p2_role if c not in used_champions]
        p2_available = [c for c in p2_champs_for_p1_role if c not in used_champions]
        
        return len(p1_available) > 0 and len(p2_available) > 0
    
    def assign_champions_to_team(self, team, used_champions=None):
        """
        Assign champions to a team, with role swapping if needed
        
        Args:
            team: List of players with roles assigned
            used_champions: Set of already used champion names
        
        Returns:
            tuple: (team_with_champions, updated_used_champions, success)
        """
        if used_champions is None:
            used_champions = set()
        else:
            used_champions = used_champions.copy()
        
        team_with_champions = []
        unassigned_players = []
        
        # First pass: Try to assign champions to players
        for player in team:
            role = player['role']
            owned_champions = player.get('owned_champions', [])
            
            # Get available champions for this role
            available_champions = self.get_owned_champions_for_role(owned_champions, role)
            available_champions = [c for c in available_champions if c not in used_champions]
            
            if available_champions:
                # Assign random champion
                champion = random.choice(available_champions)
                player_copy = player.copy()
                player_copy['champion'] = champion
                team_with_champions.append(player_copy)
                used_champions.add(champion)
            else:
                # Can't assign champion, try swapping later
                unassigned_players.append(player)
        
        # Second pass: Try to swap roles for unassigned players
        for unassigned in unassigned_players:
            swapped = False
            
            # Try swapping with each assigned player
            for i, assigned in enumerate(team_with_champions):
                if self.can_swap_roles(unassigned, assigned, used_champions):
                    # Perform the swap
                    # Remove old champion from used set
                    used_champions.remove(assigned['champion'])
                    
                    # Swap roles
                    old_role = unassigned['role']
                    unassigned['role'] = assigned['role']
                    assigned['role'] = old_role
                    
                    # Assign new champions
                    unassigned_champs = self.get_owned_champions_for_role(
                        unassigned.get('owned_champions', []),
                        unassigned['role']
                    )
                    unassigned_champs = [c for c in unassigned_champs if c not in used_champions]
                    
                    assigned_champs = self.get_owned_champions_for_role(
                        assigned.get('owned_champions', []),
                        assigned['role']
                    )
                    assigned_champs = [c for c in assigned_champs if c not in used_champions]
                    
                    if unassigned_champs and assigned_champs:
                        unassigned['champion'] = random.choice(unassigned_champs)
                        assigned['champion'] = random.choice(assigned_champs)
                        
                        used_champions.add(unassigned['champion'])
                        used_champions.add(assigned['champion'])
                        
                        # Update the assigned player in the list
                        team_with_champions[i] = assigned
                        team_with_champions.append(unassigned)
                        
                        swapped = True
                        break
            
            if not swapped:
                # Still can't assign - give them any random champion for their role
                all_role_champions = self.get_champions_for_role(unassigned['role'])
                available = [c for c in all_role_champions if c not in used_champions]
                
                if available:
                    champion = random.choice(available)
                    player_copy = unassigned.copy()
                    player_copy['champion'] = champion
                    team_with_champions.append(player_copy)
                    used_champions.add(champion)
                else:
                    # Worst case: give any champion
                    all_champions = list(self.champion_roles.keys())
                    available_any = [c for c in all_champions if c not in used_champions]
                    if available_any:
                        champion = random.choice(available_any)
                        player_copy = unassigned.copy()
                        player_copy['champion'] = champion
                        team_with_champions.append(player_copy)
                        used_champions.add(champion)
        
        return team_with_champions, used_champions, len(team_with_champions) == len(team)
    
    def assign_champions(self, team1, team2):
        """
        Assign champions to both teams ensuring no duplicates
        
        Args:
            team1: List of players with roles
            team2: List of players with roles
        
        Returns:
            dict: {
                'team1': team1_with_champions,
                'team2': team2_with_champions,
                'success': bool
            }
        """
        used_champions = set()
        
        # Assign to team 1
        team1_result, used_champions, success1 = self.assign_champions_to_team(team1, used_champions)
        
        # Assign to team 2
        team2_result, used_champions, success2 = self.assign_champions_to_team(team2, used_champions)
        
        return {
            'team1': team1_result,
            'team2': team2_result,
            'success': success1 and success2
        }

# Global instance
champion_randomizer = ChampionRandomizer()

