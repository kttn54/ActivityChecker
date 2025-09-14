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
SEND_TIME = "09:00"  # Time to send daily message (24-hour format)

# Create bot instance with necessary intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# Define a view with Yes/No buttons
class CheckInView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # View persists, no timeout

    @discord.ui.button(label="✅ Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{interaction.user.name} clicked YES at {timestamp}")
        await interaction.response.send_message("You checked in ✅", ephemeral=True)

    @discord.ui.button(label="❌ No", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{interaction.user.name} clicked NO at {timestamp}")
        await interaction.response.send_message("You checked in ❌", ephemeral=True)


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
            message = f"{date_str}: Activity Completed?"

            # Send message with buttons
            await channel.send(message, view=CheckInView())
            print(f"Daily check-in sent at {current_time}")

        # Wait 60 seconds to avoid sending multiple messages in the same minute
        await asyncio.sleep(60)


# Run the bot
if __name__ == "__main__":
    client.run(TOKEN)
