import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from config import DISCORD_TOKEN
from player_manager import player_manager
from team_randomizer import team_randomizer
from champion_randomizer import champion_randomizer
from image_generator import image_generator
from keep_alive import keep_alive

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store last randomization per channel for re-roll
last_randomizations = {}

@bot.event
async def on_ready():
    """Bot startup event"""
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.tree.command(name="register", description="Register a player for League randomizer")
@app_commands.describe(user="The Discord user to register")
async def register(interaction: discord.Interaction, user: discord.Member):
    """Register a player"""
    success, message = player_manager.register_player(user.id, user.display_name)
    
    if success:
        await interaction.response.send_message(f"✅ {message}")
    else:
        await interaction.response.send_message(f"❌ {message}")

@bot.tree.command(name="unregister", description="Unregister a player")
@app_commands.describe(user="The Discord user to unregister")
async def unregister(interaction: discord.Interaction, user: discord.Member):
    """Unregister a player"""
    success, message = player_manager.unregister_player(user.id)
    
    if success:
        await interaction.response.send_message(f"✅ {message}")
    else:
        await interaction.response.send_message(f"❌ {message}")

@bot.tree.command(name="list-players", description="Show all registered League players")
async def list_players(interaction: discord.Interaction):
    """List all registered players"""
    players = player_manager.get_all_players()
    
    if not players:
        await interaction.response.send_message("❌ No registered players yet.")
        return
    
    embed = discord.Embed(title="🎮 Registered League Players", color=discord.Color.blue())
    
    for discord_id, data in players.items():
        embed.add_field(
            name=data['discord_name'],
            value="✅ Registered",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="randomize", description="Create random teams with role assignments")
async def randomize(interaction: discord.Interaction):
    """Randomize teams without champions"""
    await interaction.response.defer()
    
    # Check if user is in a voice channel
    if not interaction.user.voice:
        await interaction.followup.send("❌ You need to be in a voice channel!")
        return
    
    voice_channel = interaction.user.voice.channel
    
    # Get members in voice channel
    vc_members = [member for member in voice_channel.members if not member.bot]
    
    if not vc_members:
        await interaction.followup.send("❌ No one in the voice channel!")
        return
    
    # Filter for registered players
    vc_member_ids = [member.id for member in vc_members]
    registered_players = player_manager.get_registered_players_in_list(vc_member_ids)
    
    if not registered_players:
        await interaction.followup.send("❌ No registered League players in the voice channel!")
        return
    
    player_count = len(registered_players)
    
    # Check if valid player count
    if not team_randomizer.is_valid_player_count(player_count):
        await interaction.followup.send(
            f"❌ Invalid player count: {player_count}\n"
            f"Required: 6 (3v3), 8 (4v4), or 10 (5v5)"
        )
        return
    
    # Create teams and assign roles
    result = team_randomizer.randomize_teams(registered_players)
    
    if not result:
        await interaction.followup.send("❌ Error creating teams")
        return
    
    # Store for re-roll
    last_randomizations[interaction.channel_id] = {
        'players': registered_players,
        'vc_members': vc_members,
        'with_champions': False
    }
    
    # Generate image
    image = await image_generator.create_full_image(
        result['team1'],
        result['team2'],
        result['game_mode'],
        result['random_role'],
        with_champions=False,
        vc_members=vc_members
    )
    
    # Convert to Discord file
    image_bytes = image_generator.image_to_bytes(image)
    file = discord.File(fp=image_bytes, filename='teams.png')
    
    # Create embed
    mode_name = result['game_mode']['name']
    embed = discord.Embed(
        title=f"🎮 {mode_name} Teams Created!",
        color=discord.Color.green(),
        description="Use `/reroll` to randomize again with same players"
    )
    
    if result['random_role']:
        embed.description += f"\nRandom role selected: **{result['random_role']}**"
    
    embed.set_image(url="attachment://teams.png")
    
    await interaction.followup.send(embed=embed, file=file)

@bot.tree.command(name="randomize-champion", description="Create random teams with champions")
async def randomize_champion(interaction: discord.Interaction):
    """Randomize teams with champion assignments"""
    await interaction.response.defer()
    
    # Check if user is in a voice channel
    if not interaction.user.voice:
        await interaction.followup.send("❌ You need to be in a voice channel!")
        return
    
    voice_channel = interaction.user.voice.channel
    
    # Get members in voice channel
    vc_members = [member for member in voice_channel.members if not member.bot]
    
    if not vc_members:
        await interaction.followup.send("❌ No one in the voice channel!")
        return
    
    # Filter for registered players
    vc_member_ids = [member.id for member in vc_members]
    registered_players = player_manager.get_registered_players_in_list(vc_member_ids)
    
    if not registered_players:
        await interaction.followup.send("❌ No registered League players in the voice channel!")
        return
    
    player_count = len(registered_players)
    
    # Check if valid player count
    if not team_randomizer.is_valid_player_count(player_count):
        await interaction.followup.send(
            f"❌ Invalid player count: {player_count}\n"
            f"Required: 6 (3v3), 8 (4v4), or 10 (5v5)"
        )
        return
    
    # Create teams and assign roles
    result = team_randomizer.randomize_teams(registered_players)
    
    if not result:
        await interaction.followup.send("❌ Error creating teams")
        return
    
    # Assign champions
    champion_result = champion_randomizer.assign_champions(result['team1'], result['team2'])
    
    if not champion_result['success']:
        await interaction.followup.send("⚠️ Warning: Some champion assignments may have failed")
    
    # Store for re-roll
    last_randomizations[interaction.channel_id] = {
        'players': registered_players,
        'vc_members': vc_members,
        'with_champions': True
    }
    
    # Generate image
    image = await image_generator.create_advanced_image_with_portraits(
        champion_result['team1'],
        champion_result['team2'],
        result['game_mode'],
        result['random_role'],
        vc_members=vc_members
    )
    
    # Convert to Discord file
    image_bytes = image_generator.image_to_bytes(image)
    file = discord.File(fp=image_bytes, filename='teams_with_champions.png')
    
    # Create embed
    mode_name = result['game_mode']['name']
    embed = discord.Embed(
        title=f"🎮 {mode_name} Teams with Champions!",
        color=discord.Color.gold(),
        description="Use `/reroll` to randomize again with same players"
    )
    
    if result['random_role']:
        embed.description += f"\nRandom role selected: **{result['random_role']}**"
    
    embed.set_image(url="attachment://teams_with_champions.png")
    
    await interaction.followup.send(embed=embed, file=file)

@bot.tree.command(name="reroll", description="Re-randomize teams with the same players")
async def reroll(interaction: discord.Interaction):
    """Re-roll the last randomization"""
    await interaction.response.defer()
    
    # Check if there's a previous randomization
    if interaction.channel_id not in last_randomizations:
        await interaction.followup.send(
            "❌ No previous randomization found!\n"
            "Use `/randomize` or `/randomize-champion` first."
        )
        return
    
    last_data = last_randomizations[interaction.channel_id]
    registered_players = last_data['players']
    with_champions = last_data['with_champions']
    vc_members = last_data.get('vc_members', [])
    
    # Create new teams with same players
    result = team_randomizer.randomize_teams(registered_players)
    
    if not result:
        await interaction.followup.send("❌ Error creating teams")
        return
    
    if with_champions:
        # Assign new champions
        champion_result = champion_randomizer.assign_champions(result['team1'], result['team2'])
        
        # Generate image with champions
        image = await image_generator.create_advanced_image_with_portraits(
            champion_result['team1'],
            champion_result['team2'],
            result['game_mode'],
            result['random_role'],
            vc_members=vc_members
        )
        
        # Convert to Discord file
        image_bytes = image_generator.image_to_bytes(image)
        file = discord.File(fp=image_bytes, filename='teams_reroll.png')
        
        # Create embed
        mode_name = result['game_mode']['name']
        embed = discord.Embed(
            title=f"🔄 {mode_name} Teams Re-rolled!",
            color=discord.Color.gold(),
            description="Use `/reroll` again to randomize once more"
        )
        
        if result['random_role']:
            embed.description += f"\nRandom role selected: **{result['random_role']}**"
    else:
        # Generate image without champions
        image = await image_generator.create_full_image(
            result['team1'],
            result['team2'],
            result['game_mode'],
            result['random_role'],
            with_champions=False,
            vc_members=vc_members
        )
        
        # Convert to Discord file
        image_bytes = image_generator.image_to_bytes(image)
        file = discord.File(fp=image_bytes, filename='teams_reroll.png')
        
        # Create embed
        mode_name = result['game_mode']['name']
        embed = discord.Embed(
            title=f"🔄 {mode_name} Teams Re-rolled!",
            color=discord.Color.green(),
            description="Use `/reroll` again to randomize once more"
        )
        
        if result['random_role']:
            embed.description += f"\nRandom role selected: **{result['random_role']}**"
    
    embed.set_image(url="attachment://teams_reroll.png")
    await interaction.followup.send(embed=embed, file=file)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"Error: {error}")

# Run the bot
async def main():
    # Start keep-alive server (for free hosting)
    keep_alive()
    
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

