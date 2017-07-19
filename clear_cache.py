from itertools import chain

from data import data_path


def clean():
    logs = data_path.joinpath('logs')
    dumps = data_path.joinpath('dumps')
    for file in chain(logs.iterdir(), dumps.iterdir()):
        if not file.name.startswith('.'):
            try:
                file.unlink()
            except (FileNotFoundError, ValueError, OSError):
                continue


if __name__ == '__main__':
    clean()
