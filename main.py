import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

RESPONSES = ["Yes", "Ho ho ho", "No", "Ben", "Ugh"]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.strip()

    if content.lower().startswith("ben") or bot.user.mentioned_in(message):
        await message.channel.send(random.choice(RESPONSES))

    await bot.process_commands(message)

bot.run(token, log_handler=handler)
