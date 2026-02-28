import discord
from discord.ext import commands
import json
import os
import asyncio
import time

# ===== CONFIG =====
TOKEN = os.environ.get('TOKEN')
OWNER_ID = 361069640962801664
PREFIX = "-"
START_TIME = time.time()

# ===== BOT SETUP =====
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Auto-react storage
auto_react = {}

# Load data
try:
    with open('auto_react.json', 'r') as f:
        auto_react = json.load(f)
except FileNotFoundError:
    auto_react = {}

def save_data():
    with open('auto_react.json', 'w') as f:
        json.dump(auto_react, f, indent=4)

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
    
    # Auto-react system
    for user_id, data in auto_react.items():
        if message.author.id == int(user_id):
            try:
                await message.add_reaction(data['emoji'])
            except:
                pass
    
    await bot.process_commands(message)

# ===== HELPER FUNCTIONS =====
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

# ===== PREFIX COMMANDS =====
@bot.command()
@commands.is_owner()
async def ar(ctx, user: discord.Member, emoji: str):
    """Auto-react to a user's messages"""
    auto_react[str(user.id)] = {'emoji': emoji, 'set_by': ctx.author.id}
    save_data()
    await ctx.send(f"Now auto-reacting to {user.name} with {emoji}")

@bot.command()
@commands.is_owner()
async def unar(ctx, user: discord.Member):
    """Remove auto-react from a user"""
    if str(user.id) in auto_react:
        del auto_react[str(user.id)]
        save_data()
        await ctx.send(f"Stopped auto-reacting to {user.name}")
    else:
        await ctx.send(f"{user.name} is not being auto-reacted to")

@bot.command()
@commands.is_owner()
async def arlist(ctx):
    """List all auto-reacted users"""
    if not auto_react:
        await ctx.send("No users are being auto-reacted to")
        return
    
    msg = "Watched users:\n"
    for user_id, data in auto_react.items():
        user = bot.get_user(int(user_id))
        if user:
            msg += f"- {user.name}: {data['emoji']}\n"
    
    await ctx.send(msg)

@bot.command()
async def ping(ctx):
    """Check bot latency"""
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def uptime(ctx):
    """Show how long the bot has been running"""
    uptime_str = get_uptime()
    await ctx.send(f"ALYA has been running for: {uptime_str}")

# ===== SLASH COMMANDS =====
@bot.tree.command(name="ping", description="Check bot latency")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")

@bot.tree.command(name="uptime", description="Show how long the bot has been running")
async def slash_uptime(interaction: discord.Interaction):
    uptime_str = get_uptime()
    await interaction.response.send_message(f"ALYA has been running for: {uptime_str}")

@bot.tree.command(name="ar", description="Auto-react to a user's messages (owner only)")
async def slash_ar(interaction: discord.Interaction, user: discord.Member, emoji: str):
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("Only the owner can use this command", ephemeral=True)
    
    auto_react[str(user.id)] = {'emoji': emoji, 'set_by': interaction.user.id}
    save_data()
    await interaction.response.send_message(f"Now auto-reacting to {user.name} with {emoji}")

@bot.tree.command(name="unar", description="Remove auto-react from a user (owner only)")
async def slash_unar(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("Only the owner can use this command", ephemeral=True)
    
    if str(user.id) in auto_react:
        del auto_react[str(user.id)]
        save_data()
        await interaction.response.send_message(f"Stopped auto-reacting to {user.name}")
    else:
        await interaction.response.send_message(f"{user.name} is not being auto-reacted to")

@bot.tree.command(name="arlist", description="List all auto-reacted users (owner only)")
async def slash_arlist(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("Only the owner can use this command", ephemeral=True)
    
    if not auto_react:
        await interaction.response.send_message("No users are being auto-reacted to")
        return
    
    msg = "Watched users:\n"
    for user_id, data in auto_react.items():
        user = bot.get_user(int(user_id))
        if user:
            msg += f"- {user.name}: {data['emoji']}\n"
    
    await interaction.response.send_message(msg)

# ===== RUN BOT =====
if __name__ == "__main__":
    print("Starting ALYA...")
    
    if not os.path.exists('auto_react.json'):
        with open('auto_react.json', 'w') as f:
            json.dump({}, f)
    
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("Invalid token")
    except Exception as e:

        print(f"Error: {e}")

