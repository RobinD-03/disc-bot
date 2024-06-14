import discord
from yt_search import search
import asyncio
import yt_dlp as youtube_dl
from dotenv import load_dotenv
import os
from keep_alive import keep_alive

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

voice_clients = {}

yt_dl_options = {
    'format':'bestaudio/best'
}

ytdl = youtube_dl.YoutubeDL(yt_dl_options)

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

client = discord.Client(intents=intents)

queue = []

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

class MusicBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = []

        self.yt_dl_options = {
            'format': 'bestaudio/best'
        }

        self.ytdl = youtube_dl.YoutubeDL(self.yt_dl_options)

        self.ffmpeg_options = {
            'options': '-vn',
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        }

    async def on_ready(self):
        print(f'We have logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if message.content.startswith('!play'):
            await self.play_song(message)

        if message.content.startswith('!skip'):
            await self.skip_song(message)

    async def play_song(self, message):
        try:
            song = message.content[len('!play'):].strip()
            song_id = search(song)
            if not song_id:
                await message.channel.send("Song not found.")
                return

            url = f"https://www.youtube.com/watch?v={song_id}"

            voice_client = message.guild.voice_client
            if voice_client:
                await voice_client.move_to(message.author.voice.channel)
            else:
                voice_client = await message.author.voice.channel.connect()

            data = await asyncio.get_event_loop().run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
            song_url = data['url']
            player = discord.FFmpegPCMAudio(song_url, **self.ffmpeg_options, executable="C:\\ffmpeg\\bin\\ffmpeg.exe")

            self.queue.append((player, url))

            if not voice_client.is_playing():
                self.play_next_in_queue(voice_client)
                await message.channel.send(f"Now playing: {url}")
            else:
                await message.channel.send(f"Added to queue: {url}")

        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")

    async def skip_song(self, message):
        try:
            voice_client = message.guild.voice_client
            if voice_client and voice_client.is_playing():
                voice_client.stop()
                await message.channel.send("Skipped the current song.")
            self.play_next_in_queue(voice_client)
        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")

    def play_next_in_queue(self, voice_client):
        if self.queue:
            player, url = self.queue.pop(0)
            voice_client.play(player, after=lambda e: self.play_next_in_queue(voice_client))
            asyncio.run_coroutine_threadsafe(self.send_now_playing_message(voice_client, url), self.loop)
        else:
            asyncio.run_coroutine_threadsafe(self.send_queue_empty_message(voice_client), self.loop)

    async def send_now_playing_message(self, voice_client, url):
        
        await message.channel.send(f"Now playing: {url}")

    async def send_queue_empty_message(self, voice_client):
        
        await message.channel.send("Queue is empty. Stopping playback.")
        await voice_client.disconnect()

intents = discord.Intents.default()
intents.message_content = True

keep_alive()

client = MusicBot(intents=intents)
client.run(os.getenv('TOKEN'))