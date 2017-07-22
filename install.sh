#!/bin/sh
git clone https://github.com/Rapptz/discord.py
cd discord.py
git fetch
git checkout rewrite
pip install .
cd ..