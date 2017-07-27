from itertools import chain

from data import data_path


def clean(include=None):
    names = ('logs', 'dumps', 'music_cache')
    if include:
        for name in include:
            assert name in names
        names = include
    it = chain(*(data_path.joinpath(n).iterdir() for n in names))
    for file in it:
        if not file.name.startswith('.'):
            try:
                file.unlink()
            except (FileNotFoundError, ValueError, OSError):
                continue


if __name__ == '__main__':
    clean()
