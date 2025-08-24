import discord
from discord.ext import tasks
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # Your bot token
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Your channel ID
SEND_TIME = "20:47"  # Time to send daily message (24-hour format)

# Create bot instance with necessary intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    # Start the daily task
    daily_checkin.start()

@tasks.loop(minutes=1)
async def daily_checkin():
    """Check every minute if it's time to send the daily message"""
    now = datetime.now(ZoneInfo("Australia/Sydney"))
    current_time = now.strftime("%H:%M")
    
    # Check if it's the right time to send
    if current_time == SEND_TIME:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            # Format date as DD/MM/YY
            date_str = now.strftime("%d/%m/%y")
            message = f"**{date_str}: Activity Completed?**"
            
            # Send message and add reaction options
            sent_message = await channel.send(message)
            await sent_message.add_reaction("✅")  # Yes
            await sent_message.add_reaction("❌")  # No
            
            print(f"Daily check-in sent at {current_time}")
        
        # Wait 60 seconds to avoid sending multiple messages in the same minute
        await asyncio.sleep(60)

@client.event
async def on_reaction_add(reaction, user):
    """Optional: Log when someone reacts to track responses"""
    # Ignore bot's own reactions
    if user == client.user:
        return
    
    # Check if this is a reaction to today's check-in
    if reaction.message.author == client.user:
        if "Activity Completed?" in reaction.message.content:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{user.name} responded with {reaction.emoji} at {timestamp}")

# Run the bot
if __name__ == "__main__":
    client.run(TOKEN)
