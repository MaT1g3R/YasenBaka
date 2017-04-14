"""A file of all helper functions"""
import json
from codecs import open as copen
from os import listdir
from os.path import isfile, join


def fopen_generic(filepath, filemode='rU', coding='utf8', buffering=-1):
    """
    Reads files using system seperators with friendly encodings
    :param filepath: file path
    :type filepath: str
    :param filemode: file mode (default 'rU')
    :type filemode: str
    :param coding: encoding for file (default 'utf8')
    :type coding: str
    :param buffering: buffer mode, 
    see https://docs.python.org/2/library/functions.html#open (default -1)
    :type buffering: int
    :return file pointer
    :rtype file
    """
    if isfile(filepath):
        return copen(filepath, filemode, coding, 'replace', buffering)
    return None


def freadlines(fp, keep_open=False):
    """
    Splits file lines
    :param fp: file pointer
    :param keep_open: keep fp open (default false)
    :type fp: file
    :type keep_open: bool | int
    :return: file lines
    :rtype: list
    """
    if fp is not None:
        lines = fp.readlines()
        if not keep_open:
            fp.close()
        return lines
    return []


def read_all_files(path):
    """
    Reads all files in a folder
    :param path: the path to the folder
    :return: All path of the files
    :rtype: list
    """
    return [join(path, f) for
            f in listdir(path) if isfile(join(path, f))]


def read_json(fp, keep_open=False):
    """
    Read a json file into a dictionary
    :param fp: the file pointer
    :type fp: file
    :param keep_open: keep file open (default False)
    :type keep_open: bool | int
    :return: the dictionary
    :rtype: dict
    """
    if fp is not None:
        data = json.load(fp)
        if not keep_open:
            fp.close()
        return data
    return {}


def write_json(fp, data, keep_open=False):
    """
    Write a dictionary into a json file
    :param fp: The json file
    :type fp: ffile
    :param data: The dictionary
    :type data: dict
    :param keep_open: keep file open (default False)
    :type keep_open: bool | int
    :return: nothing
    :rtype: None
    """
    if fp is not None:
        json.dump(data, fp)
        if not keep_open:
            fp.close()
