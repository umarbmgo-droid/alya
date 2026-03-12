import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio
import time
from typing import List, Optional

# ===== CONFIG =====
TOKEN = os.environ.get('TOKEN')
OWNER_ID = 361069640962801664
START_TIME = time.time()

# ===== BOT SETUP =====
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=None, intents=intents, help_command=None)  # No prefix commands

# Data storage
auto_react = {}  # user_id: {"emojis": ["😈", "👍"], "set_by": owner_id}
admins = []  # List of admin user IDs

# Load data
def load_data():
    global auto_react, admins
    try:
        with open('auto_react.json', 'r') as f:
            auto_react = json.load(f)
    except FileNotFoundError:
        auto_react = {}
    
    try:
        with open('admins.json', 'r') as f:
            admins = json.load(f)
    except FileNotFoundError:
        admins = []

def save_data():
    with open('auto_react.json', 'w') as f:
        json.dump(auto_react, f, indent=4)
    with open('admins.json', 'w') as f:
        json.dump(admins, f, indent=4)

load_data()

# ===== HELPER FUNCTIONS =====
def is_owner_or_admin(user_id):
    return user_id == OWNER_ID or user_id in admins

def get_uptime():
    current_time = time.time()
    uptime_seconds = int(current_time - START_TIME)
    
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)

async def resolve_emoji(emoji_input, guild):
    """Convert emoji input to usable emoji - works with custom emojis from any server"""
    # If it's a custom emoji in format <:name:id> or <a:name:id>
    if emoji_input.startswith('<') and emoji_input.endswith('>'):
        # Extract emoji ID
        animated = emoji_input.startswith('<a:')
        parts = emoji_input.split(':')
        if len(parts) >= 3:
            emoji_id = parts[2].replace('>', '')
            # Try to get emoji from any guild the bot is in
            for g in bot.guilds:
                emoji = discord.utils.get(g.emojis, id=int(emoji_id))
                if emoji:
                    return emoji
            # If not found, return the raw string (might still work)
            return emoji_input
    return emoji_input

# ===== STATUS =====
async def status_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Umar"
        ))
        await asyncio.sleep(60)

# ===== EVENTS =====
@bot.event
async def on_ready():
    print("="*50)
    print("ALYA IS ONLINE")
    print(f"Bot ID: {bot.user.id}")
    print(f"Servers: {len(bot.guilds)}")
    print(f"Admins: {len(admins)}")
    print(f"Auto-reacted users: {len(auto_react)}")
    print("="*50)
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Failed to sync: {e}")
    
    bot.loop.create_task(status_loop())

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Auto-react system - SUPER FAST with multiple emojis
    if str(message.author.id) in auto_react:
        data = auto_react[str(message.author.id)]
        for emoji in data['emojis']:
            try:
                # Try to resolve the emoji
                resolved = await resolve_emoji(emoji, message.guild)
                await message.add_reaction(resolved)
            except:
                pass
    
    await bot.process_commands(message)

# ===== SLASH COMMANDS =====

# Admin commands group
admin_group = app_commands.Group(name="admin", description="Admin management commands")

@admin_group.command(name="add", description="Add a user as admin")
async def admin_add(interaction: discord.Interaction, user: discord.Member):
    """Add a user as admin (owner only)"""
    if interaction.user.id != OWNER_ID:
        embed = discord.Embed(
            description="Only the owner can use this command",
            color=0x000000
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if user.id in admins:
        embed = discord.Embed(
            description=f"{user.mention} is already an admin",
            color=0x000000
        )
        return await interaction.response.send_message(embed=embed)
    
    admins.append(user.id)
    save_data()
    
    embed = discord.Embed(
        description=f"{user.mention} is now an admin",
        color=0x000000
    )
    await interaction.response.send_message(embed=embed)

@admin_group.command(name="remove", description="Remove admin from a user")
async def admin_remove(interaction: discord.Interaction, user: discord.Member):
    """Remove admin from a user (owner only)"""
    if interaction.user.id != OWNER_ID:
        embed = discord.Embed(
            description="Only the owner can use this command",
            color=0x000000
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if user.id not in admins:
        embed = discord.Embed(
            description=f"{user.mention} is not an admin",
            color=0x000000
        )
        return await interaction.response.send_message(embed=embed)
    
    admins.remove(user.id)
    save_data()
    
    embed = discord.Embed(
        description=f"{user.mention} is no longer an admin",
        color=0x000000
    )
    await interaction.response.send_message(embed=embed)

@admin_group.command(name="list", description="List all admins")
async def admin_list(interaction: discord.Interaction):
    """List all admins"""
    if not is_owner_or_admin(interaction.user.id):
        embed = discord.Embed(
            description="You don't have permission to use this command",
            color=0x000000
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    owner = bot.get_user(OWNER_ID)
    owner_text = f"👑 {owner.mention}" if owner else f"👑 Owner ({OWNER_ID})"
    
    admin_text = "\n".join([f"• {bot.get_user(admin).mention}" for admin in admins if bot.get_user(admin)])
    
    embed = discord.Embed(
        description=f"{owner_text}\n{admin_text}" if admins else f"{owner_text}\nNo other admins",
        color=0x000000
    )
    await interaction.response.send_message(embed=embed)

# Auto-react commands group
react_group = app_commands.Group(name="react", description="Auto-react management commands")

@react_group.command(name="add", description="Add auto-reactions to a user (up to 4 emojis)")
@app_commands.describe(user="User to auto-react to", emoji1="First emoji", emoji2="Second emoji (optional)", emoji3="Third emoji (optional)", emoji4="Fourth emoji (optional)")
async def react_add(
    interaction: discord.Interaction, 
    user: discord.Member, 
    emoji1: str,
    emoji2: Optional[str] = None,
    emoji3: Optional[str] = None,
    emoji4: Optional[str] = None
):
    """Add auto-reactions to a user (owner/admins only)"""
    if not is_owner_or_admin(interaction.user.id):
        embed = discord.Embed(
            description="You don't have permission to use this command",
            color=0x000000
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Collect emojis
    emojis = [emoji1]
    if emoji2:
        emojis.append(emoji2)
    if emoji3:
        emojis.append(emoji3)
    if emoji4:
        emojis.append(emoji4)
    
    # Limit to 4
    emojis = emojis[:4]
    
    # Verify emojis work
    working_emojis = []
    for e in emojis:
        resolved = await resolve_emoji(e, interaction.guild)
        if resolved:
            working_emojis.append(e)
    
    auto_react[str(user.id)] = {
        'emojis': working_emojis,
        'set_by': interaction.user.id
    }
    save_data()
    
    emoji_display = " ".join(working_emojis)
    embed = discord.Embed(
        description=f"Now auto-reacting to {user.mention} with {emoji_display}",
        color=0x000000
    )
    await interaction.response.send_message(embed=embed)

@react_group.command(name="remove", description="Remove auto-reactions from a user")
async def react_remove(interaction: discord.Interaction, user: discord.Member):
    """Remove auto-reactions from a user (owner/admins only)"""
    if not is_owner_or_admin(interaction.user.id):
        embed = discord.Embed(
            description="You don't have permission to use this command",
            color=0x000000
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if str(user.id) in auto_react:
        del auto_react[str(user.id)]
        save_data()
        embed = discord.Embed(
            description=f"Stopped auto-reacting to {user.mention}",
            color=0x000000
        )
    else:
        embed = discord.Embed(
            description=f"{user.mention} is not being auto-reacted to",
            color=0x000000
        )
    
    await interaction.response.send_message(embed=embed)

@react_group.command(name="list", description="List all auto-reacted users")
async def react_list(interaction: discord.Interaction):
    """List all auto-reacted users (owner/admins only)"""
    if not is_owner_or_admin(interaction.user.id):
        embed = discord.Embed(
            description="You don't have permission to use this command",
            color=0x000000
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if not auto_react:
        embed = discord.Embed(
            description="No users are being auto-reacted to",
            color=0x000000
        )
        return await interaction.response.send_message(embed=embed)
    
    description = ""
    for user_id, data in auto_react.items():
        user = bot.get_user(int(user_id))
        if user:
            emojis = " ".join(data['emojis'])
            description += f"• {user.mention}: {emojis}\n"
    
    embed = discord.Embed(
        description=description,
        color=0x000000
    )
    await interaction.response.send_message(embed=embed)

# Basic commands
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(
        description=f"{round(bot.latency * 1000)}ms",
        color=0x000000
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="uptime", description="Show how long the bot has been running")
async def uptime(interaction: discord.Interaction):
    uptime_str = get_uptime()
    embed = discord.Embed(
        description=uptime_str,
        color=0x000000
    )
    await interaction.response.send_message(embed=embed)

# Register groups
bot.tree.add_command(admin_group)
bot.tree.add_command(react_group)

# ===== RUN BOT =====
if __name__ == "__main__":
    print("Starting ALYA...")
    
    if not os.path.exists('auto_react.json'):
        with open('auto_react.json', 'w') as f:
            json.dump({}, f)
    
    if not os.path.exists('admins.json'):
        with open('admins.json', 'w') as f:
            json.dump([], f)
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("Invalid token")
    except Exception as e:
        print(f"Error: {e}")


