import asyncio
import functools
import itertools
import math
import random

import discord
import yt_dlp as youtube_dl
from async_timeout import timeout
from discord.ext import commands
from discord.ext import tasks

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass
    

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Now playing',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            """if self.loop:
                while True:
                    await self.current.souce.channel.send(embed=self.current.create_embed())
                    self.voice.play(self.current.source, after=self.current.source)
                    await self.next.wait()"""
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            try: raise VoiceError(str(error))
            except: pass

        self.next.set()

    def skip(self):
        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}
        self.inactivity_check.start()

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state
        print(self.voice_states)

        return state

    @staticmethod
    def cog_check(ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    @commands.command(name='join', invoke_without_subcommand=True, aliases=["j", "summon"])
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            return await ctx.voice_state.voice.move_to(destination)

        ctx.voice_state.voice = await destination.connect()
        await ctx.send(f"Successfully moved to `{destination}`")

    @commands.command(name='leave', aliases=['disconnect', "l", "d"])
    async def leave(self, ctx: commands.Context):
        if not ctx.voice_state.voice or not ctx.author.voice.channel:
            return await ctx.send('Not connected to any voice channel.')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]
        await ctx.send(f"Successfully left `{ctx.author.voice.channel}`")

    @commands.command(name='volume', description="Sets the volume of the player", aliases=["vol"])
    async def volume(self, ctx: commands.Context, *, volume: int):
        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        if 0 > volume > 100 or not volume:
            return await ctx.send('Volume must be between 0 and 100')

        ctx.voice_state.volume = volume / 100
        await ctx.send(':notes: Volume of the player set to **{}%**'.format(volume))

    @commands.command(name='nowplaying', description="Sends info on the song currently playing", aliases=['current', 'playing', "np", "now", "now_playing"])
    async def now(self, ctx: commands.Context):
        try: await ctx.send(embed=ctx.voice_state.current.create_embed())
        except: await ctx.send(":notes: No song currently playing.")

    @commands.command(name='pause', description="Pauses the player")
    async def pause(self, ctx: commands.Context):
        try:
            if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
                ctx.voice_state.voice.pause()
                await ctx.message.add_reaction('⏯')
                await ctx.send(f"Successfully paused {ctx.voice_state.current.source.title}")
            else:
                await ctx.reply(":notes: No song currently playing.")
        except AttributeError:
            await ctx.send(":notes: No song currently playing.")

    @commands.command(name='resume', description="Resumes the player", aliases=["res"])
    async def resume(self, ctx: commands.Context):
        try:
            if ctx.voice_state.voice.is_paused():
                ctx.voice_state.voice.resume()
                await ctx.message.add_reaction('⏯')
                await ctx.send(f"Successfully resumed **{ctx.voice_state.current.source.title}**")
            else:
                await ctx.reply(":notes: No song currently playing.")
        except AttributeError:
            await ctx.send(":notes: No song currently playing.")

    @commands.command(name='stop', description="Clears the queue and leaves the voice channel")
    async def stop(self, ctx: commands.Context):
        ctx.voice_state.songs.clear()
        try:
            if not ctx.voice_state.voice or not ctx.author.voice.channel:
                return await ctx.send('Not connected to any voice channel.')
            await ctx.invoke(self.skip)
            await ctx.invoke(self.leave)
            await ctx.message.add_reaction('⏹️')
        except:
            await ctx.reply(":notes: No song currently playing and no songs in queue.")

    @commands.command(name='skip', description="Skips the current song", aliases=["s"])
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now...')

        ctx.voice_state.skip()
        await ctx.send(f":notes: Skipped **{ctx.voice_state.current.source.title}** - {ctx.voice_state.current.requester.mention}")

    @commands.command(name='queue', description="Shows the full queue", aliases=["q"])
    async def queue(self, ctx: commands.Context, *, page: int = 1):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def shuffle(self, ctx: commands.Context):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove')
    async def remove(self, ctx: commands.Context, index: int):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')


    @commands.command(name='loop')
    async def loop(self, ctx: commands.Context, loop: bool = None):
        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')
        if not loop:
            ctx.voice_state.loop = not ctx.voice_state.loop
        else:
            ctx.voice_state.loop = loop
        await ctx.send(f"Successfully set `loop` to `{ctx.voice_state.loop}`.")

    @commands.command(name='play')
    async def play(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_state.voice:
            await ctx.invoke(self.join)

        if not ctx.author.voice or not ctx.author.voice.channel:
            return
    
        if ctx.author.voice and ctx.author.voice.self_deaf:
            return await ctx.send(":ear: You need to be undeafened to enqueue a song.")

        async with ctx.typing():
            try:
                if search == "gautham":
                    search = "batman gotham city"
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
            else:
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                await ctx.send('Enqueued {}'.format(str(source)))

    @join.before_invoke
    @play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply('You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                return await ctx.reply('Bot is already in a voice channel.')
    
    @tasks.loop(minutes=5)
    async def inactivity_check(self):
        if len(self.voice_states) > 0:
            for i in list(self.voice_states):
                if self.voice_states[i].voice:
                    if not self.voice_states[i].is_playing and not self.voice_states[i].voice.is_playing():
                        await self.voice_states[i].stop()
                        del self.voice_states[i]
                        print(self.voice_states)
    
            
async def setup(bot):
    await bot.add_cog(Music(bot))
