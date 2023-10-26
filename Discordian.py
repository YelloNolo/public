import discord
from discord.ext import commands
import cv2
import asyncio
import os
import ffmpeg

TOKEN = "enter_discord_token_here"
VIDEO_FOLDER = "videos" # The video folder path

intents = discord.Intents.default()
intents.typing = False

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user:
        return

    # Watches for user entering VC
    if before.channel is None and after.channel is not None:
        voice_channel = after.channel
        if not member.bot:
            voice_client = await voice_channel.connect()
            await play_video_audio(voice_client)

    # Watches for user exiting VC
    elif before.channel is not None and after.channel is None:
        voice_channel = before.channel
        if not member.bot and len(voice_channel.members) == 1 and voice_channel.members[0] == bot.user:
            await voice_channel.guild.voice_client.disconnect()

    # Watches for user switching VC
    elif before.channel is not None and after.channel is not None:
        # Disconnect from previous channel if only bot is left
        prev_voice_channel = before.channel
        if len(prev_voice_channel.members) == 1 and prev_voice_channel.members[0] == bot.user:
            await prev_voice_channel.guild.voice_client.disconnect()

        # Bot join channel
        new_voice_channel = after.channel
        if not member.bot:
            voice_client = await new_voice_channel.connect()
            await play_video_audio(voice_client)


# Convert '.mp4' to '.mp3', (video playback is work in progress)
async def play_video_audio(voice_client):
    for filename in os.listdir(VIDEO_FOLDER):
        if filename.endswith(".mp4"):
            video_path = os.path.join(VIDEO_FOLDER, filename)
            audio_path = video_path.replace(".mp4", ".mp3")
            # Extract audio from '.mp4'
            ffmpeg.input(video_path).output(audio_path).run(overwrite_output=True)  # Extract audio from '.mp4' with overwrite
            # Play extracted audio in voice channel
            voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=audio_path))


bot.run(TOKEN)