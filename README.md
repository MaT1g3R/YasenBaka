# YasenBaka  
Yasen-Baka discord bot, written with the [discord.py](https://github.com/Rapptz/discord.py) api.  
You can invite the bot to your channel with this [link](https://discordapp.com/oauth2/authorize?client_id=243230010532560896&scope=bot&permissions=-1)  
Join the support server [here](https://discord.gg/BnPbz6q)  
# Commands
* #### Moderation commands:
```
pmall, setprefix
```
* #### World of Warship commands:
```
addshame, removeshame, shame, shamelist
```

* #### Fun commadns:  
```
ayaya, chensaw, choose, joke, kanna, kyubey, lewd, osu, place, repeat, roll, salt, umi
```

* #### Utility commands:
```
anime, avatar, currency, info, joined, latex, ping, prefix, stackoverflow, systeminfo
```

* #### Music commands:
```
pause, play, playing, resume, skip, stop, summon, volume
```
* #### NSFW commands:
```
danbooru, gelbooru, konachan, yandere
```
You can also talk to the bot by mentioning her!

# Self Host
To self host yasen, you will need those packages installed on your system:
* Python3.6+: https://www.python.org/downloads/ Python3.5 and below is not supported
* FFmpeg: https://ffmpeg.org/
* SQLite3: https://www.sqlite.org/


In addition, you will need to execute the following command to install required libraries:

First cd into the directory where yasen is located, then:
```
$ pip3 install cffi
$ pip3 install -r requirements.txt
```
On Linux, you might run into trouble installing PyNaCl, please refer to the below image.

[logo]: 
https://camo.githubusercontent.com/70c57a8abd17504a36554c87290f864be48686ea/687474703a2f2f692e696d6775722e636f6d2f35625165584a582e706e67 

Then you will need to rename ``sample_mydb`` to ``mydb`` in the ``data`` directory and rename ``sample_api.py`` to ``api.py`` in the ``config`` directory, and fill out the api keys inside.

Then to run, execute ``yasen-baka.py`` in the root directory with a python3.6+ interpreter, or execute ``run.sh`` on GNU/Linux or MacOS, ``run.bat`` on Microsoft<sup>®</sup> Windows<sup>®</sup>.