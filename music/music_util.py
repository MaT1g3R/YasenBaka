from asyncio import get_event_loop
from collections import Iterable
from functools import partial
from os.path import isfile
from pathlib import Path
from typing import Optional, Union

from discord import Embed
from discord.ext.commands import Context
from mutagen import MutagenError
from mutagen.easymp4 import EasyMP4
from mutagen.flac import FLAC
from mutagen.mp3 import EasyMP3
from youtube_dl import YoutubeDL


def add_embed_options(embed: Embed) -> Embed:
    embed.add_field(name='Previous Page', value=':rewind:')
    embed.add_field(name='Next Page', value=':fast_forward:')
    embed.add_field(name='Exit', value=':x:')
    embed.set_footer(text='This message will self destruct after'
                          '1 minute of inactivity.')
    return embed


def __to_string(tag: Union[str, list, None]) -> Optional[str]:
    """
    Function to turn a tag into a string.
    :param tag: the tag.
    :return: the tag as a string.
    """
    if isinstance(tag, str):
        res = tag.strip()
    elif isinstance(tag, Iterable):
        res = ', '.join(tag).strip()
    else:
        res = None
    if isinstance(res, str):
        return res or None
    return None


def get_file_info(file_path: str) -> tuple:
    """
    Get mp3/mp4/flac tags from a file.
    :param file_path: the file path.
    :return: a tuple of  (title, genre, artist, album, length)
    """
    empty = lambda: (Path(file_path).name, None, None, None, None)
    tag = None
    try:
        if file_path.endswith('.flac'):
            tag = FLAC(file_path)
        elif file_path.endswith('.mp3'):
            tag = EasyMP3(file_path)
        elif file_path.endswith('m4a'):
            tag = EasyMP4(file_path)
        else:
            return empty()
        get = lambda t, s: t.get(s, None) or t.get(s.upper(), None)
        title = get(tag, 'title') or Path(file_path).name
        genre = get(tag, 'genre')
        artist = get(tag, 'artist')
        album = get(tag, 'album')
        length = tag.info.length
        if isinstance(length, (int, float)):
            minutes, seconds = divmod(length, 60)
            length_str = f'{int(minutes)}:{round(seconds):02d}'
        else:
            length_str = None
        return (__to_string(title), __to_string(genre),
                __to_string(artist), __to_string(album), length_str)
    except MutagenError:
        return empty()
    finally:
        del tag


def file_detail(title, genre, artist, album, length) -> str:
    """
    :return: a detailed string repersentation of a file audio source.
    """
    artist = f'\nArtist:\n`{artist}`' if artist else ''
    album = f'\nAlbum:\n`{album}\n`' if album else ''
    genre = f'\nGenre:\n`{genre}`' if genre else ''
    length = f' [{length}]' if length else ''
    return f'\t{title}{length}\n{artist}\n{album}\n{genre}'


def get_ytdl_format(out_format):
    return {
        'format': 'bestaudio/best',
        'outtmpl': out_format,
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }


async def fetch_ytdl_info(ytdl: YoutubeDL, query: str) -> dict:
    """
    Fetch video data using YoutubeDL.
    :param ytdl: the YoutubeDL instance.
    :param query: the search query.
    :return: the video data.
    """
    loop = get_event_loop()
    func = partial(ytdl.extract_info, query, download=False)
    data = await loop.run_in_executor(None, func)
    return data


def ytdl_detail(title, duration, uploader, requester, date) -> str:
    """
    :return: a detailed string repersentation of a youtube-dl audio source.
    """
    try:
        duration = float(duration)
    except (TypeError, ValueError):
        length = ''
    else:
        hours, seconds = divmod(duration, 3600)
        minutes, seconds = divmod(seconds, 60)
        hours_str = f'{int(hours):02d}:' if hours else ''
        length = f' [{hours_str}{int(minutes):02d}:{int(seconds):02d}]'
    uploader = f'\nUploaded by: `{uploader}`' if uploader else ''
    date = f'\tUpload date: `{date}`' if date else ''
    return (f'\n{title}{length}\tRequested by: `{requester}`'
            f'{uploader}{date}')


async def yt_download(ydl: YoutubeDL, data: dict,
                      logger, webpage_url: str) -> str:
    """
    Download a file from youtube dl.
    :param ydl: the `YoutubeDL` instance.
    :param data: the file data.
    :param logger: the logger to do logging with.
    :param webpage_url: the webpage url.
    :return: the file path to the download.
    """
    loop = get_event_loop()
    file_path = ydl.prepare_filename(data)
    if isfile(file_path):
        logger.info(
            f'File {file_path} found, not downloading.'
        )
        return file_path
    logger.info(f'Downloading {webpage_url}')
    await loop.run_in_executor(
        None, ydl.download, [webpage_url]
    )
    logger.info(
        f'{webpage_url} downloaded to {file_path}'
    )
    return file_path


def playlist_embed(ctx: Context, cur_page: int, total_page: int,
                   current, section: list) -> Optional[Embed]:
    """
    Get an embed representation of a section of a audio playlist.

    :param ctx: the `discord.Context` object.

    :param cur_page: the current page number.

    :param total_page: the total page count.

    :param current: the currently playing `Entry`
    :type current: Entry

    :param section: a list of `Entry` in the section.
    :type section: List[Entry]

    :return: An embed representation of a section of a audio playlist, if any.
    """
    if not section and not current:
        return
    colour = ctx.bot.config.colour
    embed = Embed(
        colour=colour,
        title=f'Playlist page {cur_page} of {total_page}'
    )
    embed.add_field(
        name='Currently Playing',
        value=str(current),
        inline=False
    )
    if section:
        section_str = '\n'.join(
            f'{i+1+((cur_page -1)* 10)}. {entry}'
            for i, entry in enumerate(section)
        )
        embed.add_field(name='Up Next', value=section_str, inline=False)
    return embed
