import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
import asyncio

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.getLogger('discord').setLevel(logging.WARNING)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

RESPONSES = ["Yes", "Ho ho ho", "No", "Ben", "Ugh"]
AUDIO_RESPONSES = ["Yes", "Ho ho ho", "No", "Ben", "Ugh", "Burp", "Taunt"]
AUDIO_DIR = "./audio"
BEN_CHANNEL_NAME = "Ben"

if not discord.opus.is_loaded():
    try:
        discord.opus.load_opus('libopus.so.0')  # Linux/Pi
    except:
        discord.opus.load_opus('/opt/homebrew/lib/libopus.dylib')  # Mac

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    # auto join Ben vc
    for guild in bot.guilds:
        channel = discord.utils.get(guild.voice_channels, name=BEN_CHANNEL_NAME)
        if channel:
            members = [m for m in channel.members if not m.bot]
            if members: # only join if someone is already there
                vc = await channel.connect()
                bot.loop.create_task(play_random_loop(vc))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.strip()

    if content.lower().startswith("ben") or bot.user.mentioned_in(message):
        await message.channel.send(random.choice(RESPONSES))

    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user:
        return

    # someone joined BEN_CHANNEL_NAME channel
    if after.channel and after.channel.name == BEN_CHANNEL_NAME:
        vc = discord.utils.get(bot.voice_clients, guild=member.guild)

        # if not connected, Ben joins channel
        if not vc or not vc.is_connected():
            vc = await after.channel.connect()
            bot.loop.create_task(play_random_loop(vc))

        # Wait for for any current audio to finish
        while vc.is_playing():
            await asyncio.sleep(0.3)

        play_audio(vc, "Ben")
    
    # someone left BEN_CHANNEL_NAME channel
    if before.channel and before.channel.name == BEN_CHANNEL_NAME:
        members = [m for m in before.channel.members if not m.bot]
        if not members:
            vc = discord.utils.get(bot.voice_clients, guild=member.guild)
            if vc and vc.is_connected():
                await vc.disconnect()

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

def play_audio(vc, choice):
    audio_path = os.path.join(AUDIO_DIR, f"{choice}.ogg")
    if os.path.exists(audio_path):
        vc.play(discord.FFmpegPCMAudio(audio_path))

async def play_random_loop(vc):
    while vc.is_connected():
        # wait between 5-60s to play audio
        wait = random.randint(5, 60)
        await asyncio.sleep(wait)

        if not vc.is_connected():
            break

        # Check if anyone else is in channel (excluding Ben)
        members = [m for m in vc.channel.members if not m.bot]
        if not members:
            continue
        
        if not vc.is_playing():
            choice = random.choice(AUDIO_RESPONSES)
            play_audio(vc, choice)

bot.run(token, log_handler=handler)
