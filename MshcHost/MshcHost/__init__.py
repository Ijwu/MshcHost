"""
The flask application package.
"""

from flask import Flask
from os import environ, getcwd, mkdir
from os.path import join, isdir, basename, splitext

import zipfile
import MshcHost.index as index
from logging import StreamHandler
from sys import stdout


app = Flask(__name__)
app.logger.setLevel(10)  # debug
app.logger.addHandler(StreamHandler(stdout))

cache_path = join(getcwd(), "filecache")
if not isdir(cache_path):
    mkdir(cache_path)
default_path = join(getcwd(), "help.mshc")
try:
    path = environ.get("MSHC_PATH", default_path)
except ValueError:
    path = default_path
cache = join(cache_path, splitext(basename(path))[0])


def unzip_mshc(path, cache_path):
    app.logger.info("Unzipping MSHC content. This may take a while.")
    final_cache = join(cache_path, splitext(basename(path))[0])
    if not isdir(final_cache):
        mkdir(final_cache)
    with zipfile.ZipFile(path) as zip:
        zip.extractall(final_cache)


def init_index(mshc_path):
    index.initialize(mshc_path)


def initialize():
    if not isdir(cache):
        unzip_mshc(path, cache_path)
    init_index(cache)


app.logger.info("Initializing...")
initialize()

from MshcHost import views

if __name__ == "__main__":
    pass
