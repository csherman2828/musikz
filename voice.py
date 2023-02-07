import asyncio
import itertools
import random

import discord
from async_timeout import timeout
from discord.ext import commands
import httpx
from bs4 import BeautifulSoup

import ytdl


class VoiceError(Exception):
    pass


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: ytdl.YTDLSource):
        print('voice.Song.__init__', source.title)
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        print('voice.Song.create_embed', self.source.title)
        embed = discord.Embed(title='Now playing', description='```css\n{0.source.title}\n```'.format(self), color=discord.Color.blurple())
                #  .add_field(name='Duration', value=self.source.duration)
                #  .add_field(name='Requested by', value=self.requester.mention)
                #  .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                #  .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                #  .set_thumbnail(url=self.source.thumbnail)
                #  .set_author(name=self.requester.name, icon_url=self.requester.avatar_url))
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
        print('voice.SongQueue.clear')
        self._queue.clear()

    def shuffle(self):
        print('voice.SongQueue.shuffle')
        random.shuffle(self._queue)

    def remove(self, index: int):
        print('voice.SongQueue.remove', index)
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        print('voice.VoiceState.__init')
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.song_history = []
        self.exists = True

        self._loop = False
        # FIXME keep autoplay false - it's broken, throws no error, and freezes 
        #     the bot
        self._autoplay = False
        self._volume = 0.5

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        print('voice.VoiceState.__del__')
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def autoplay(self):
        return self._autoplay

    @autoplay.setter
    def autoplay(self, value: bool):
        self._autoplay = value

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
            print('voice.VoiceState.audio_player_task', 'at loop beginning')
            self.next.clear()
            self.now = None

            if self.loop == False:
                print('voice.VoiceState.audio_player_task', 'song is not looped')
                # If autoplay is turned on wait 3 seconds for a new song.
                # If no song is found find a new one,
                # else if autoplay is turned off try to get the
                # next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                # FIXME autoplay is broken right now
                if self.autoplay and self.current and False:
                    try:
                        print('voice.VoiceState.audio_player_task', 'autoplaying - wait 3 seconds for a song')
                        async with timeout(3):
                            self.current = await self.songs.get()
                    except asyncio.TimeoutError:
                        
                        print('voice.VoiceState.audio_player_task', 'no song received, finding recommendation to autoplay')
                        # Spoof user agent to show whole page.
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'}
                        song_url = self.current.source.url
                        # Get the page
                        print('voice.VoiceState.audio_player_task', 'getting webpage for song url', song_url)
                        async with httpx.AsyncClient() as client:
                            response = await client.get(song_url, headers=headers)
  
                        print('voice.VoiceState.audio_player_task', 'doing beautiful soup things')
                        # FIXME gets stuck after this line, never prints
                        #     'got soup'
                        soup = BeautifulSoup(response.text, features='lxml')
                        print('got soup')

                        # Parse all the recommended videos out of the response and store them in a list
                        recommended_urls = []
                        for li in soup.find_all('li', class_='related-list-item'):
                            a = li.find('a')

                            # Only videos (no mixes or playlists)
                            if 'content-link' in a.attrs['class']:
                                print('appending url', f'https://www.youtube.com{a.get("href")}')
                                recommended_urls.append(
                                    f'https://www.youtube.com{a.get("href")}')

                        ctx = self._ctx

                        # Chose the next song so that it wasnt played recently

                        print('choosing next song')

                        next_song = recommended_urls[0]

                        for recommended_url in recommended_urls:
                            not_in_history = True
                            for song in self.song_history[:15]:
                                if recommended_url == song.source.url:
                                    not_in_history = False
                                    break

                            if not_in_history:
                                next_song = recommended_url
                                break

                        
                        print('voice.VoiceState.audio_player_task', 'found next song', next_song)
                        async with ctx.typing():
                            try:
                                source = await ytdl.YTDLSource.create_source(ctx, next_song, loop=self.bot.loop)
                            except ytdl.YTDLError as e:
                                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
                                self.bot.loop.create_task(self.stop())
                                self.exists = False
                                return
                            else:
                                song = Song(source)
                                self.current = song
                                await ctx.send('Autoplaying {}'.format(str(source)))

                else:
                    print('voice.VoiceState.audio_player_task', 'no autoplay')
                    try:
                        print('voice.VoiceState.audio_player_task', 'waiting 3 minutes before disconnecting')
                        async with timeout(180):  # 3 minutes
                            self.current = await self.songs.get()
                    except asyncio.TimeoutError:
                        
                        print('voice.VoiceState.audio_player_task', '3 minutes passed - disconnecting')
                        self.bot.loop.create_task(self.stop())
                        self.exists = False
                        return

                
                print('voice.VoiceState.audio_player_task', 'playing next song')
                self.song_history.insert(0, self.current)
                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)
                await self.current.source.channel.send(embed=self.current.create_embed())

            # If the song is looped
            elif self.loop == True:
                print('voice.VoiceState.audio_player_task', 'song is looped, playing again')
                self.song_history.insert(0, self.current)
                self.now = discord.FFmpegPCMAudio(
                    self.current.source.stream_url, **ytdl.YTDLSource.FFMPEG_OPTIONS)
                self.voice.play(self.now, after=self.play_next_song)

        
            print('voice.VoiceState.audio_player_task', 'waiting for end of current song')
            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None
