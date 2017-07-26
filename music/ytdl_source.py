from datetime import datetime

from discord import FFmpegPCMAudio, PCMVolumeTransformer

from music.abstract_source import AbstractSource


class YTDLSource(AbstractSource):
    __slots__ = ('requester',)

    def __init__(self, pcm: FFmpegPCMAudio, fname: str, data: dict):
        """
        :param pcm: a FFmpegPCMAudio object.
        :param fname: the file name.
        :param data: a dictionary of music meta data.
        """
        title = data.get('title', fname)
        duration = data.get('duration')
        uploader = data.get('uploader')
        self.requester = data['requester']
        date = data.get('upload_date')
        if date:
            try:
                date = datetime.strptime(date, '%Y%M%d').date()
            except ValueError:
                date = None
        super().__init__(
            PCMVolumeTransformer(pcm),
            title,
            self.__get_detail(title, duration, uploader, self.requester, date)
        )
        del data
        del title
        del duration
        del uploader
        del date

    def __str__(self):
        return f'{super().__str__()}\tRequested by {self.requester}'

    @staticmethod
    def __get_detail(title, duration, uploader, requester, date) -> str:
        """
        See `AbstractSource.detail`
        """
        try:
            if duration:
                duration = int(duration)
                minutes, seconds = divmod(duration, 60)
                hours = 0
                if minutes > 60:
                    hours, minutes = divmod(minutes, 60)
                length_list = []
                if hours:
                    length_list.append(f'{int(hours)}hr')
                if minutes:
                    length_list.append(f'{int(minutes):02d}min')
                length_list.append(f'{round(seconds):02d}sec')
                length = f' [{" ".join(length_list)}]'
            else:
                length = ''
        except ValueError:
            length = ''
        uploader = f'\nUploaded by: `{uploader}`' if uploader else ''
        date = f'\tUpload date: `{date}`' if date else ''
        return (
            f'\n{title}{length}\tRequested by: `{requester}`'
            f'{uploader}{date}'
        )
