from asyncio import get_event_loop
from datetime import datetime
from functools import partial
from os import remove
from os.path import isfile
from time import time

from youtube_dl import YoutubeDL

from data import data_path
from music.abstract_source import AbstractSource
from music.music_util import fetch_ytdl_info, get_ytdl_format, ytdl_detail


class YTDLSource(AbstractSource):
    """
    Audio source for youtube-dl.

    === Attributes ===
    :type data: dict
        Data dict retrived from youtube-dl.
    :type requester: str
        Song requester name.
    :type need_download: bool
        True to download the audio to local storage,
        False to use the streaming url provided by youtube-dl.
    :type delete_after: bool
        Ture will delete the file downloaded by this instance after it's
        been deleted.
    :type title: str
        Title for the audio.
    :type webpage_url:
        Webpage url for the audio source.
    :type file_path: Optional[str]
        File path to the downloaded audio, None if the audio is not downloaded.
    :type logger: Logger
        Logger to do logging.
    """
    __slots__ = ('data', 'requester', 'need_download', 'delete_after',
                 'webpage_url', 'file_path', 'title', 'logger')

    def __init__(self, data: dict, requester: str, need_download: bool,
                 delete_after: bool, logger):
        """
        :param data: The data dict provided by youtube-dl.
        :param requester: the song requester name.
        :param need_download:
            True to download the audio to local storage,
            False to use the streaming url provided by youtube-dl.
        :param delete_after:
            Ture will delete the file downloaded by this instance after it's
            been deleted.
        """
        self.data = data
        self.requester = requester
        self.need_download = need_download
        self.delete_after = delete_after
        self.title = data.get('title')
        self.webpage_url = data.get('webpage_url')
        self.file_path = None
        self.logger = logger

        duration = data.get('duration')
        uploader = data.get('uploader')
        date = data.get('upload_date')
        if date:
            try:
                date = datetime.strptime(date, '%Y%M%d').date()
            except ValueError:
                date = None

        super().__init__(
            partial(
                ytdl_detail, self.title, duration, uploader,
                self.requester, date
            )
        )

        del data
        del duration
        del uploader
        del date

    async def true_name(self) -> str:
        """
        Overrides `AbstractSource.true_name`

        If `self.need_download` is True this will wait for youtube-dl to
        download the audio data to local storage and return the file path.

        If `self.need_download` is False this will fetch the streaming url
        using youtube-dl.

        :return: Name used by `FFmpegPCMAudio`
        """
        if self.need_download:
            out_dir = 'dumps' if self.delete_after else 'music_cache'
            epoch = f'{int(time())}-' if self.delete_after else ''
            out = (f'{str(data_path.joinpath(out_dir))}'
                   f'/{epoch}%(extractor)s-%(id)s-%(title)s.%(ext)s')
            with YoutubeDL(get_ytdl_format(out)) as ydl:
                loop = get_event_loop()
                self.file_path = ydl.prepare_filename(self.data)
                if isfile(self.file_path):
                    self.logger.info(
                        f'File {self.file_path} found, not downloading.'
                    )
                    return self.file_path
                self.logger.info(f'Downloading {self.webpage_url}')
                await loop.run_in_executor(
                    None, ydl.download, [self.webpage_url]
                )
                self.logger.info(
                    f'{self.webpage_url} downloaded to {self.file_path}'
                )
                return self.file_path
        else:
            with YoutubeDL(get_ytdl_format(None)) as ydl:
                data = await fetch_ytdl_info(ydl, self.webpage_url)
                if 'entries' in data:
                    data = data['entries'][0]
            url = data['url']
            del data
            return url

    def __str__(self):
        return f'{self.title}\tRequested by {self.requester}'

    def clean_up(self):
        if self.delete_after and self.file_path is not None:
            try:
                self.logger.info(f'Deleting {self.file_path}')
                remove(self.file_path)
            except Exception as e:
                self.logger.warn(f'File {self.file_path} not deleted.\n{e}')
            else:
                self.logger.info(f'File {self.file_path} deleted.')
        del self.file_path
        del self.requester
        del self.webpage_url
        del self.need_download
        del self.data
