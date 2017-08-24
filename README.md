# YasenBaka [![Build Status](https://travis-ci.org/MaT1g3R/YasenBaka.svg?branch=master)](https://travis-ci.org/MaT1g3R/YasenBaka)
Yasen-Baka, a multifunctional Discord bot
with special World of Warships commands., written with the [discord.py](https://github.com/Rapptz/discord.py) api.  
You can invite the bot to your guild with this [link](https://discordapp.com/oauth2/authorize?client_id=243230010532560896&scope=bot&permissions=-1)  

## Notice
I no longer use discord for personal reasons. I will try to fix bugs as they come up but as of this momnet I do not plan on adding any new features.

If you  are interested in continuing this project please shoot me an email at `mat1g3r at gmail dot com` or contact me on matrix at `mat1g3r@matrix.org`.

## Usage

To get started with the bot, simply type `?help` into your guild channel.

Commands are divided into 9 categories, they are listed below.


  * #### Bot Info Commands:

    ```
    help, info, ping, prefix reset, prefix set, prefix
    ```

  * #### Fun Commands:

    ```
    choose, repeat, roll, salt
    ```

  * #### Moderation Commands:  

    ```
    masspm, purge
    ```

  * #### Music Commands:

    ```
    play, playdefault, playing, playlist, setskip, skip, stop
    ```

  * #### Nsfw Commands:

    ```
    danbooru, e621, gelbooru, konachan, rule34, yandere
    ```

  * #### Osu Commands:

    ```
    osu
    ```

  * #### Utility Commands:

    ```
    avatar, currency, joined, latex, stackoverflow
    ```

  * #### Weeb Commands:

    ```
    LN, anime, ayaya, chensaw, joke, kanna, karen, manga, safebooru, umi
    ```

  * #### World of Warships Commands:

    ```
    clan, shame, shamelist add, shamelist remove, shamelist
    ```


## Self Host
To self host yasen, you will need those packages installed on your system:
* Python3.6+: https://www.python.org/downloads/ Python3.5 and below is not supported
* FFmpeg: https://ffmpeg.org/
* SQLite3: https://www.sqlite.org/

In addition, you will need to execute the following command to install required libraries:

First cd into the directory where yasen is located, then:

```bash
pip install -Ur requirements.txt
```

Make a copy of `YasenBaka/data/sample_db` in the `YasenBaka/data/` directory and rename it to `yasen_db`

Make a copy of `YasenBaka/config/sample_config.json` in the `YasenBaka/config/` directory and rename it to `config.json`. Then you will need to fill out the required config values and api keys. I am not responsible for helping you obtaining any of the api keys.

Finally to run, do:
```bash
python3 yasen-baka.py
```

## Contributing
For non-developers, you can contribute by reporting bugs or making suggestions.
Simply open a Github issue [here](https://github.com/MaT1g3R/YasenBaka/issues/new)

For developers, if you are interested in contributing, follow the steps below:
1. Fork it ( https://github.com/MaT1g3R/YasenBaka/fork )
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)
5. Create a new Pull Request
