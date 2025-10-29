from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import aiohttp
import os
from config import SUMMONERS_RIFT_IMAGE, ROLE_POSITIONS

class ImageGenerator:
    def __init__(self):
        self.default_font_size = 16
        self.title_font_size = 40
        self.champion_size = 70
        self.profile_size = 45
        self.map_size = 512  # Standard map dimension
        
    def create_circular_image(self, image, size):
        """Convert square image to circular"""
        # Resize
        image = image.resize((size, size), Image.Resampling.LANCZOS)
        
        # Create circular mask
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        
        # Apply mask
        output = ImageOps.fit(image, (size, size), centering=(0.5, 0.5))
        output.putalpha(mask)
        
        return output
    
    async def download_image(self, url):
        """Download image from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        return Image.open(io.BytesIO(image_data)).convert('RGBA')
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")
        return None
    
    async def get_discord_avatar(self, user_id, vc_members):
        """Get Discord user avatar"""
        try:
            # Find the member object from vc_members
            for member in vc_members:
                if str(member.id) == str(user_id):
                    avatar_url = member.display_avatar.url
                    return await self.download_image(avatar_url)
        except Exception as e:
            print(f"Error fetching Discord avatar: {e}")
        return None
    
    async def get_champion_portrait(self, champion_name):
        """Get champion portrait from Riot Data Dragon (free API - no key needed)"""
        try:
            # Data Dragon doesn't need API key - it's free!
            # We'll use the champion name to build the URL
            # Format: https://ddragon.leagueoflegends.com/cdn/VERSION/img/champion/CHAMPIONNAME.png
            # For now, we'll use a recent version
            version = "13.24.1"  # Update this periodically or fetch dynamically
            url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champion_name}.png"
            return await self.download_image(url)
        except Exception as e:
            print(f"Error fetching champion portrait: {e}")
        return None
    
    def get_font(self, size):
        """Get font (fallback to default if custom font not available)"""
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            try:
                return ImageFont.truetype("Arial.ttf", size)
            except:
                try:
                    # Try Windows font path
                    return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size)
                except:
                    return ImageFont.load_default()
    
    def load_map_image(self):
        """Load and resize the Summoner's Rift map"""
        try:
            if os.path.exists(SUMMONERS_RIFT_IMAGE):
                map_img = Image.open(SUMMONERS_RIFT_IMAGE).convert('RGBA')
                # Resize to standard size
                map_img = map_img.resize((self.map_size, self.map_size), Image.Resampling.LANCZOS)
                return map_img
            else:
                # Create fallback colored background
                return Image.new('RGBA', (self.map_size, self.map_size), (20, 40, 30, 255))
        except Exception as e:
            print(f"Error loading map image: {e}")
            return Image.new('RGBA', (self.map_size, self.map_size), (20, 40, 30, 255))
    
    async def create_team_image(self, team_data, team_name, with_champions=False, vc_members=None):
        """
        Create image for one team on the Summoner's Rift map
        
        Args:
            team_data: List of players with roles (and champions if with_champions=True)
            team_name: "Team 1" or "Team 2"
            with_champions: Whether to include champion portraits
        
        Returns:
            PIL Image
        """
        # Load map as background
        map_img = self.load_map_image()
        
        # Create canvas with map and space for title
        canvas_width = self.map_size
        canvas_height = self.map_size + 80  # Extra space for title
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (15, 20, 25, 255))
        
        # Paste map below title area
        canvas.paste(map_img, (0, 80), map_img)
        
        draw = ImageDraw.Draw(canvas)
        title_font = self.get_font(32)
        text_font = self.get_font(self.default_font_size)
        small_font = self.get_font(12)
        
        # Draw team name at top with background
        title_bbox = draw.textbbox((0, 0), team_name, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_height = title_bbox[3] - title_bbox[1]
        
        # Draw semi-transparent background for title
        draw.rectangle([(0, 0), (canvas_width, 70)], fill=(0, 0, 0, 200))
        draw.text((canvas_width // 2, 35), team_name, fill='gold', font=title_font, anchor='mm')
        
        # Overlay player portraits on map positions
        for player in team_data:
            role = player['role']
            if role not in ROLE_POSITIONS:
                continue
            
            # Get position on map (adjusted for title offset)
            x, y = ROLE_POSITIONS[role]
            y += 80  # Offset for title area
            
            if with_champions and 'champion' in player:
                # Draw champion portrait background (square)
                champion_bg_size = self.champion_size
                champion_x = x - champion_bg_size // 2
                champion_y = y - champion_bg_size // 2
                
                # Try to get actual champion portrait
                champion_img = await self.get_champion_portrait(player['champion'])
                
                if champion_img:
                    # Resize and use actual champion portrait
                    champion_bg = champion_img.resize((champion_bg_size, champion_bg_size), Image.Resampling.LANCZOS)
                    
                    # Add gold border
                    border_img = Image.new('RGBA', (champion_bg_size, champion_bg_size), (255, 215, 0, 255))
                    border_draw = ImageDraw.Draw(border_img)
                    border_draw.rectangle([(3, 3), (champion_bg_size-4, champion_bg_size-4)], 
                                        fill=(0, 0, 0, 0))
                    champion_bg.paste(border_img, (0, 0), border_img)
                else:
                    # Fallback to placeholder
                    champion_bg = Image.new('RGBA', (champion_bg_size, champion_bg_size), (30, 30, 40, 255))
                    champ_draw = ImageDraw.Draw(champion_bg)
                    champ_draw.rectangle([(0, 0), (champion_bg_size-1, champion_bg_size-1)], 
                                        outline='gold', width=3)
                    champ_name = player['champion'][:8]
                    champ_draw.text((champion_bg_size // 2, champion_bg_size // 2), 
                                   champ_name, fill='white', font=small_font, anchor='mm')
                
                canvas.paste(champion_bg, (champion_x, champion_y), champion_bg)
                
                # Draw profile picture (circular, overlapping bottom-right)
                profile_offset = int(self.champion_size * 0.6)
                profile_x = x + profile_offset - self.profile_size // 2
                profile_y = y + profile_offset - self.profile_size // 2
                
                # Try to get actual Discord avatar
                avatar_img = None
                if vc_members and 'discord_id' in player:
                    avatar_img = await self.get_discord_avatar(player['discord_id'], vc_members)
                
                if avatar_img:
                    # Make circular and resize
                    profile_bg = self.create_circular_image(avatar_img, self.profile_size)
                    
                    # Add white border
                    border_size = self.profile_size + 4
                    border = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
                    border_draw = ImageDraw.Draw(border)
                    border_draw.ellipse([(0, 0), (border_size-1, border_size-1)], 
                                       outline='white', width=3)
                    
                    # Combine
                    final_profile = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
                    final_profile.paste(profile_bg, (2, 2), profile_bg)
                    final_profile.paste(border, (0, 0), border)
                    
                    canvas.paste(final_profile, (profile_x-2, profile_y-2), final_profile)
                else:
                    # Fallback placeholder
                    profile_bg = Image.new('RGBA', (self.profile_size, self.profile_size), (50, 50, 50, 255))
                    profile_draw = ImageDraw.Draw(profile_bg)
                    profile_draw.ellipse([(0, 0), (self.profile_size-1, self.profile_size-1)], 
                                        fill=(70, 70, 80, 255), outline='white', width=2)
                    canvas.paste(profile_bg, (profile_x, profile_y), profile_bg)
                
                # Draw username below with background
                username = player.get('discord_name', 'Unknown')
                if len(username) > 12:
                    username = username[:10] + ".."
                
                text_bbox = draw.textbbox((0, 0), username, font=text_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                text_y = y + champion_bg_size // 2 + 10
                
                # Background for text
                draw.rectangle([(x - text_width//2 - 5, text_y - text_height//2 - 2),
                               (x + text_width//2 + 5, text_y + text_height//2 + 2)],
                              fill=(0, 0, 0, 180))
                
                draw.text((x, text_y), username, fill='white', font=text_font, anchor='mm')
                
                # Draw role label above
                role_y = y - champion_bg_size // 2 - 12
                role_bbox = draw.textbbox((0, 0), role, font=text_font)
                role_width = role_bbox[2] - role_bbox[0]
                role_height = role_bbox[3] - role_bbox[1]
                
                draw.rectangle([(x - role_width//2 - 5, role_y - role_height//2 - 2),
                               (x + role_width//2 + 5, role_y + role_height//2 + 2)],
                              fill=(0, 0, 0, 180))
                
                draw.text((x, role_y), role, fill='gold', font=text_font, anchor='mm')
            else:
                # Without champions, just show role and name
                # Draw profile picture
                profile_x = x - self.profile_size // 2
                profile_y = y - self.profile_size // 2
                
                # Try to get actual Discord avatar
                avatar_img = None
                if vc_members and 'discord_id' in player:
                    avatar_img = await self.get_discord_avatar(player['discord_id'], vc_members)
                
                if avatar_img:
                    # Make circular and resize
                    profile_bg = self.create_circular_image(avatar_img, self.profile_size)
                    
                    # Add gold border
                    border_size = self.profile_size + 4
                    border = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
                    border_draw = ImageDraw.Draw(border)
                    border_draw.ellipse([(0, 0), (border_size-1, border_size-1)], 
                                       outline='gold', width=3)
                    
                    # Combine
                    final_profile = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
                    final_profile.paste(profile_bg, (2, 2), profile_bg)
                    final_profile.paste(border, (0, 0), border)
                    
                    canvas.paste(final_profile, (profile_x-2, profile_y-2), final_profile)
                else:
                    # Fallback placeholder
                    profile_bg = Image.new('RGBA', (self.profile_size, self.profile_size), (50, 50, 50, 255))
                    profile_draw = ImageDraw.Draw(profile_bg)
                    profile_draw.ellipse([(0, 0), (self.profile_size-1, self.profile_size-1)], 
                                        fill=(70, 70, 80, 255), outline='gold', width=2)
                    canvas.paste(profile_bg, (profile_x, profile_y), profile_bg)
                
                # Draw username below
                username = player.get('discord_name', 'Unknown')
                if len(username) > 12:
                    username = username[:10] + ".."
                
                text_y = y + self.profile_size // 2 + 12
                text_bbox = draw.textbbox((0, 0), username, font=text_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                draw.rectangle([(x - text_width//2 - 5, text_y - text_height//2 - 2),
                               (x + text_width//2 + 5, text_y + text_height//2 + 2)],
                              fill=(0, 0, 0, 180))
                
                draw.text((x, text_y), username, fill='white', font=text_font, anchor='mm')
                
                # Draw role above
                role_y = y - self.profile_size // 2 - 12
                role_bbox = draw.textbbox((0, 0), role, font=text_font)
                role_width = role_bbox[2] - role_bbox[0]
                role_height = role_bbox[3] - role_bbox[1]
                
                draw.rectangle([(x - role_width//2 - 5, role_y - role_height//2 - 2),
                               (x + role_width//2 + 5, role_y + role_height//2 + 2)],
                              fill=(0, 0, 0, 180))
                
                draw.text((x, role_y), role, fill='gold', font=text_font, anchor='mm')
        
        return canvas
    
    async def create_full_image(self, team1_data, team2_data, game_mode, random_role=None, with_champions=False, vc_members=None):
        """
        Create single map image with both teams (Team 1 on blue side, Team 2 on red side)
        
        Args:
            team1_data: List of players with roles (and champions)
            team2_data: List of players with roles (and champions)
            game_mode: Game mode info dict
            random_role: For 4v4, which role was selected
            with_champions: Whether to include champion portraits
            vc_members: List of Discord members for avatar fetching
        
        Returns:
            PIL Image
        """
        # Load single map as background
        map_img = self.load_map_image()
        
        # Create canvas with map and space for header
        header_height = 100
        canvas_width = self.map_size
        canvas_height = self.map_size + header_height
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (15, 20, 25, 255))
        
        # Add header with match info
        draw = ImageDraw.Draw(canvas)
        title_font = self.get_font(40)
        subtitle_font = self.get_font(20)
        team_label_font = self.get_font(24)
        
        # Draw header background
        draw.rectangle([(0, 0), (canvas_width, header_height - 10)], fill=(0, 0, 0, 200))
        
        # Main title
        mode_text = f"{game_mode['name']} Match"
        draw.text((canvas_width // 2, 35), mode_text, fill='gold', font=title_font, anchor='mm')
        
        # Subtitle with random role info if applicable
        if random_role:
            subtitle = f"Random Role: {random_role}"
            draw.text((canvas_width // 2, 70), subtitle, fill='lightblue', font=subtitle_font, anchor='mm')
        
        # Paste map below header
        canvas.paste(map_img, (0, header_height), map_img)
        
        # Draw team labels on the map
        # Team 1 label (Blue side - bottom left)
        draw.text((80, header_height + 30), "Team 1", fill='dodgerblue', font=team_label_font, anchor='mm')
        
        # Team 2 label (Red side - top right)
        draw.text((canvas_width - 80, header_height + self.map_size - 30), "Team 2", fill='orangered', font=team_label_font, anchor='mm')
        
        # Draw Team 1 (Blue side) - use original positions
        await self._draw_team_on_map(canvas, team1_data, header_height, False, with_champions, vc_members, 'dodgerblue')
        
        # Draw Team 2 (Red side) - mirror positions
        await self._draw_team_on_map(canvas, team2_data, header_height, True, with_champions, vc_members, 'orangered')
        
        return canvas
    
    async def _draw_team_on_map(self, canvas, team_data, y_offset, mirror, with_champions, vc_members, border_color):
        """
        Helper method to draw a team's players on the map
        
        Args:
            canvas: PIL Image to draw on
            team_data: List of players with roles
            y_offset: Vertical offset for positioning (header height)
            mirror: If True, mirror positions for red team (top-right)
            with_champions: Whether to include champion portraits
            vc_members: List of Discord members
            border_color: Color for borders ('dodgerblue' or 'orangered')
        """
        draw = ImageDraw.Draw(canvas)
        text_font = self.get_font(self.default_font_size)
        small_font = self.get_font(12)
        
        for player in team_data:
            role = player['role']
            if role not in ROLE_POSITIONS:
                continue
            
            # Get base position
            base_x, base_y = ROLE_POSITIONS[role]
            
            # Mirror for Team 2 (red side)
            if mirror:
                x = self.map_size - base_x
                y = self.map_size - base_y
            else:
                x = base_x
                y = base_y
            
            # Apply y offset for header
            y += y_offset
            
            if with_champions and 'champion' in player:
                # Draw champion portrait
                champion_bg_size = self.champion_size
                champion_x = x - champion_bg_size // 2
                champion_y = y - champion_bg_size // 2
                
                champion_img = await self.get_champion_portrait(player['champion'])
                
                if champion_img:
                    champion_bg = champion_img.resize((champion_bg_size, champion_bg_size), Image.Resampling.LANCZOS)
                    
                    # Add colored border
                    border_img = Image.new('RGBA', (champion_bg_size, champion_bg_size), (0, 0, 0, 0))
                    border_draw = ImageDraw.Draw(border_img)
                    border_draw.rectangle([(0, 0), (champion_bg_size-1, champion_bg_size-1)], 
                                        outline=border_color, width=3)
                    champion_bg.paste(border_img, (0, 0), border_img)
                else:
                    champion_bg = Image.new('RGBA', (champion_bg_size, champion_bg_size), (30, 30, 40, 255))
                    champ_draw = ImageDraw.Draw(champion_bg)
                    champ_draw.rectangle([(0, 0), (champion_bg_size-1, champion_bg_size-1)], 
                                        outline=border_color, width=3)
                    champ_name = player['champion'][:8]
                    champ_draw.text((champion_bg_size // 2, champion_bg_size // 2), 
                                   champ_name, fill='white', font=small_font, anchor='mm')
                
                canvas.paste(champion_bg, (champion_x, champion_y), champion_bg)
                
                # Draw profile picture (circular, overlapping bottom-right)
                profile_offset = int(self.champion_size * 0.6)
                profile_x = x + profile_offset - self.profile_size // 2
                profile_y = y + profile_offset - self.profile_size // 2
                
                avatar_img = None
                if vc_members and 'discord_id' in player:
                    avatar_img = await self.get_discord_avatar(player['discord_id'], vc_members)
                
                if avatar_img:
                    profile_bg = self.create_circular_image(avatar_img, self.profile_size)
                    
                    # Add white border
                    border_size = self.profile_size + 4
                    border = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
                    border_draw = ImageDraw.Draw(border)
                    border_draw.ellipse([(0, 0), (border_size-1, border_size-1)], 
                                       outline='white', width=3)
                    
                    final_profile = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
                    final_profile.paste(profile_bg, (2, 2), profile_bg)
                    final_profile.paste(border, (0, 0), border)
                    
                    canvas.paste(final_profile, (profile_x-2, profile_y-2), final_profile)
                else:
                    profile_bg = Image.new('RGBA', (self.profile_size, self.profile_size), (50, 50, 50, 255))
                    profile_draw = ImageDraw.Draw(profile_bg)
                    profile_draw.ellipse([(0, 0), (self.profile_size-1, self.profile_size-1)], 
                                        fill=(70, 70, 80, 255), outline='white', width=2)
                    canvas.paste(profile_bg, (profile_x, profile_y), profile_bg)
                
                # Draw username below
                username = player.get('discord_name', 'Unknown')
                if len(username) > 12:
                    username = username[:10] + ".."
                
                text_bbox = draw.textbbox((0, 0), username, font=text_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                text_y = y + champion_bg_size // 2 + 10
                
                draw.rectangle([(x - text_width//2 - 5, text_y - text_height//2 - 2),
                               (x + text_width//2 + 5, text_y + text_height//2 + 2)],
                              fill=(0, 0, 0, 180))
                
                draw.text((x, text_y), username, fill='white', font=text_font, anchor='mm')
                
                # Draw role label above
                role_y = y - champion_bg_size // 2 - 12
                role_bbox = draw.textbbox((0, 0), role, font=text_font)
                role_width = role_bbox[2] - role_bbox[0]
                role_height = role_bbox[3] - role_bbox[1]
                
                draw.rectangle([(x - role_width//2 - 5, role_y - role_height//2 - 2),
                               (x + role_width//2 + 5, role_y + role_height//2 + 2)],
                              fill=(0, 0, 0, 180))
                
                draw.text((x, role_y), role, fill=border_color, font=text_font, anchor='mm')
            else:
                # Without champions, just show role and profile
                profile_x = x - self.profile_size // 2
                profile_y = y - self.profile_size // 2
                
                avatar_img = None
                if vc_members and 'discord_id' in player:
                    avatar_img = await self.get_discord_avatar(player['discord_id'], vc_members)
                
                if avatar_img:
                    profile_bg = self.create_circular_image(avatar_img, self.profile_size)
                    
                    border_size = self.profile_size + 4
                    border = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
                    border_draw = ImageDraw.Draw(border)
                    border_draw.ellipse([(0, 0), (border_size-1, border_size-1)], 
                                       outline=border_color, width=3)
                    
                    final_profile = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
                    final_profile.paste(profile_bg, (2, 2), profile_bg)
                    final_profile.paste(border, (0, 0), border)
                    
                    canvas.paste(final_profile, (profile_x-2, profile_y-2), final_profile)
                else:
                    profile_bg = Image.new('RGBA', (self.profile_size, self.profile_size), (50, 50, 50, 255))
                    profile_draw = ImageDraw.Draw(profile_bg)
                    profile_draw.ellipse([(0, 0), (self.profile_size-1, self.profile_size-1)], 
                                        fill=(70, 70, 80, 255), outline=border_color, width=2)
                    canvas.paste(profile_bg, (profile_x, profile_y), profile_bg)
                
                # Draw username below
                username = player.get('discord_name', 'Unknown')
                if len(username) > 12:
                    username = username[:10] + ".."
                
                text_y = y + self.profile_size // 2 + 12
                text_bbox = draw.textbbox((0, 0), username, font=text_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                draw.rectangle([(x - text_width//2 - 5, text_y - text_height//2 - 2),
                               (x + text_width//2 + 5, text_y + text_height//2 + 2)],
                              fill=(0, 0, 0, 180))
                
                draw.text((x, text_y), username, fill='white', font=text_font, anchor='mm')
                
                # Draw role above
                role_y = y - self.profile_size // 2 - 12
                role_bbox = draw.textbbox((0, 0), role, font=text_font)
                role_width = role_bbox[2] - role_bbox[0]
                role_height = role_bbox[3] - role_bbox[1]
                
                draw.rectangle([(x - role_width//2 - 5, role_y - role_height//2 - 2),
                               (x + role_width//2 + 5, role_y + role_height//2 + 2)],
                              fill=(0, 0, 0, 180))
                
                draw.text((x, role_y), role, fill=border_color, font=text_font, anchor='mm')
    
    async def create_advanced_image_with_portraits(self, team1_data, team2_data, game_mode, random_role=None, vc_members=None):
        """
        Create advanced image with champion portraits and Discord profile pictures
        
        This version fetches actual champion portraits and Discord avatars
        """
        return await self.create_full_image(team1_data, team2_data, game_mode, random_role, with_champions=True, vc_members=vc_members)
    
    def save_image(self, image, filename):
        """Save image to file"""
        try:
            image.save(filename, 'PNG')
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def image_to_bytes(self, image):
        """Convert PIL Image to bytes for Discord upload"""
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes

# Global instance
image_generator = ImageGenerator()

