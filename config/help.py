COMMAND_LISTS = [
    ('Moderation', ['pmall', 'setprefix']),

    ('World of Warships',
     ['shame', 'shamelist', 'addshame', 'removeshame', 'clan', 'clanwtr']),

    ('Fun',
     ['kyubey', 'roll', 'choose', 'salt', 'repeat', 'kanna', 'chensaw', 'lewd',
      'ayaya', 'osu', 'umi', 'place', 'joke']),

    ('Utility',
     ['latex', 'joined', 'anime', 'avatar', 'stackoverflow',
      'currency', 'info', 'ping', 'prefix', 'systeminfo']),

    ('Music',
     ['summon', 'play', 'volume', 'pause', 'resume', 'stop', 'skip',
      'playing']),

    ('NSFW', ['danbooru', 'konachan', 'yandere', 'gelbooru'])
]

COMMANDS = {
    "shame": "Looks for a player on Warships Today. "
             "You can also look up players by pinging them if they are "
             "in the shamelist. Support all regions, default is NA."
             " The region codes are: 'NA', 'EU', 'RU', 'AS' "
             "\nExample usage: `{0}shame MaT1g3R`, `{0}shame flamu EU`",
    "volume": "Sets the volume of the currently playing song."
              "\nExample usage: `{0}volume 50`",
    "addshame": "Add yourself to the shamelist. If you are already in "
                "the shamelist, it will be overwritten by the new player name."
                " Support all regions, default is NA. "
                "The region codes are: 'NA', 'EU', 'RU', 'AS'"
                "\nExample usage: "
                "`{0}addshame MY_WOWS_USER_NAME`, `{0}addshame flamu EU`",
    "currency": "Converts currency.\nExample usage: "
                "'{0}currency JPY CAD 18000' this converts 18000 JPY to CAD",
    "kanna": "Display a random Kanna image.",
    "roll": "Rolls some dice.\nExample usage: "
            "`{0}roll 3d6` This rolls 6 sided die, 3 times.",
    "stackoverflow": "Searches for an answer on stackoverflow, this feature "
                     "is highly experimental."
                     "\nExample usage: `{0}stackoverflow Python linked list`",
    "avatar": "Displays the avatar of a user. "
              "\nExample usage: `{0}avatar name`, `{0}avatar @some_mention`",
    "shamelist": "Prints out the entire shamelist for this server.",
    "salt": "Probability of something happening over some amount of tries."
            "\nExample usage: "
            "`{0}salt 0.01 100` this is the same as `{0}salt 1% 100`",
    "skip": "Vote to skip a song. The song requester can automatically skip."
            " 3 skip votes are needed for the song to be skipped.",
    "anime": "Searches for an anime on MAL."
             "\nExample usage `{0}anime Madoka Magica`",
    "playing": "Shows info about the currently played song.",
    "repeat": "Repeats text for x amout of times, max is 5 times."
              "\nExample usage: `{0}repeat 5 Dank memes`",
    "kyubey": "Kyubey",
    "play": "Plays a song.\nIf there is a song currently in the queue, then "
            "it isqueued until the next song is done playing."
            "\nThis command automatically searches as well from YouTube."
            "The list of supported sites can be found here:"
            "<https://rg3.github.io/youtube-dl/supportedsites.html>\n"
            "Example usage: `{0}play Poland is not yet lost`",
    "joined": "Show when a member joined the server,\nExample usage: "
              "`{0}joined name`, `{0}joined @mention`",
    "choose": "Choose an item between multiple items, separated by space."
              "\nExample usage: `{0}choose item1 item2 item_3`",
    "stop": "Stops playing audio and leaves the voice channel. "
            "This also clears the queue.",
    "pmall": "Sends a custom pm to all mentioned member, "
             "this is an admin only command.\nExample usage: `{0}pmall @user1 "
             "@user2 @user3 write your content after the mentions`",
    "resume": "Resumes the currently played song.",
    "summon": "Summons the bot to join your voice channel.",
    "pause": "Pauses the currently played song.",
    "latex": "Render a latex equation."
             "\nExample usage: `{0}latex \\int_0^1 \\frac{log(x)}{x^2 + 1}`",
    "removeshame": "Removes you from the shamelist.",
    "info": "Displays some info about the bot.",
    "chensaw": "Displays a spinning chensaw gif.",
    "lewd": "Displays a random lewd reaction face.",
    "ayaya": "Ayaya!",
    "osu": "Return information for an osu! user. No filter for searching in "
           "standard mode, add one of: `--osu, --Taiko, --CTB, --mania` "
           "to the end of your search to specify the mode."
           "\nExample usage: `{0}osu potateau`, `{0}osu Bukkake Blast --CTB`",
    "ping": "Shows the response time of the bot.",
    "umi": "Umi is a vile ocean.",
    "place": "Let us marvel at the greatness of the internet. "
             "\n `{0}place clean`for the cleaned up version.",
    "joke": "It's joke!",
    "setprefix": "Set the prefix of the bot for this server. This "
                 "is an admin only command. \nExample usage:`{0}setprefix !`",
    "prefix": "Display the prefix for the server, is always "
              "accessible via the default prefix.",
    "systeminfo": "Display the system info of the bot.",
    "gelbooru": "Search gelbooru for a picture. Tags are separated with spaces."
                "\nExample usage: "
                "`{0}gelbooru haruna_(kantai_collection) solo`",
    "danbooru": "Search danbooru for a picture. Tags are separated with spaces."
                "\nExample usage: "
                "`{0}danbooru haruna_(kantai_collection) solo`",
    "konachan": "Search konachan for a picture. Tags are separated with spaces."
                "\nExample usage: `{0}konachan haruna_(kancolle) wet`",
    "yandere": "Search yande.re for a picture. Tags are separated with spaces."
               "\nExample usage: `{0}yandere konachan haruna_(kancolle) wet`",
    "clan": "Look for a World of Warships clan. Support all regions, "
            "default is NA. The region codes are: 'NA', 'EU', 'RU', 'AS' "
            "\nExample usage: `{0}clan ZR`,`{0}clan OMNI EU`",
    "clanwtr": "Look for a World of Warships clan with WTR support. "
               "Support all regions, "
            "default is NA. The region codes are: 'NA', 'EU', 'RU', 'AS' "
            "\nExample usage: `{0}clanwtr ZR`,`{0}clanwtr OMNI EU`"
}
