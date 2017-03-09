## osu_apy
## Author: Daniel "Albinohat" Mercado
##
## A simple wrapper module around osu!api. https://github.com/peppy/osu-api/wiki

## Definitions
## API key           - An alpha-numeric string given to developers to authenticate their identities when using the API.
##                       NEVER give this to anyone. When using this code or the API directly, avoid putting your API Key directly in your code.
## Beatmap set       - A collection of all the difficulties for a particular song.
## Beatmap           - A single difficulty within a Beatmap Set.
## MSGQL time format - YYYY-MM-DD hh:mm:ss

## IDs
## Beatmap set ID  - A number from an https://osu.ppy.sh/s/ URL.
##                       Corresponds to a collection of difficulties for a given song.
## Beatmap ID      - A number from an https://osu.ppy.sh/b/ URL.
##                       Corresponds to a single difficulty for a given song.
## User ID         - A number or someone's username from an https://osu.ppy.sh/u/ URL.
##                       Corresponds to a user's profile.
## Multiplayer ID  - A number from an https://osu.ppy.sh/mp/ URL. Corresponds to a multiplayer match history.

## Notes
## Omitted optional parameters should be supplied as null strings.

## Standard Imports
import json, re, sys, urllib.request, urllib.parse, urllib.error


## osu!apy Methods

## build_request - Returns the full API request URL using the provided base URL and parameters.
## list_params   - The list of parameters to add to the end of the request URL.
## URL - The base API request URL to append the list of parameters to.
def build_request(list_of_params, url):
    ## Build the request URL.
    for param in list_of_params:
        url += str(param)
        if (param != ""):
            url += "&"

    ## Remove the trailing '&' because I'm OCD.
    return url[:-1]


## get_beatmaps - Returns a JSON payload containing information about a beatmap set or beatmap.
## key          - Your API key. (Required)
## since        - A MYSQL-formatted date which is the cut off for the returned data.
## set_id       - A beatmap set ID.
## beatmap_id   - A beatmap ID.
## user_id      - A user ID.
def get_beatmaps(key, since, set_id, beatmap_id, user_id):
    ## Create a list to store the attributes which are present.
    list_of_params = []

    ## Populate the list of PHP variables.
    ## Only prepend the PHP variable names if they are there.
    list_of_params.append(parameterize_key(key))
    list_of_params.append(parameterize_since(since))
    list_of_params.append(parameterize_id("s", set_id))
    list_of_params.append(parameterize_id("b", beatmap_id))
    list_of_params.append(parameterize_id("u", user_id))

    ## Build the request URLand return the response.
    return urllib.request.urlopen(build_request(list_of_params, "https://osu.ppy.sh/api/get_beatmaps?")).read()


## get_match - Returns information about multiplayer match.
## key       - Your API key. (Required)
## multi_id  - A multiplayer match ID.
def get_match(key, multi_id):
    ## Create a list to store the attributes which are present.
    list_of_params = []

    ## Populate the list of PHP variables.
    ## Only prepend the PHP variable names if they are there.
    list_of_params.append(parameterize_key(key))
    list_of_params.append(parameterize_id("mp", multi_id))

    ## Build the request URLand return the response.
    return urllib.request.urlopen(build_request(list_of_params, "https://osu.ppy.sh/api/get_beatmaps?")).read()


## get_scores - Returns information about the top 50 scores of a specified beatmap.
## key        - Your API key.
## beatmap_id - A beatmap ID.
## user_id    - A user ID.
## mode       - The game mode for which to get info.
##                  (0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania, Default = 0)
def get_scores(key, beatmap_id, user_id, mode):
    ## Create a list to store the attributes which are present.
    list_of_params = []

    ## Populate the list of PHP variables.
    ## Only prepend the PHP variable names if they are there.
    list_of_params.append(parameterize_key(key))
    list_of_params.append(parameterize_id("b", beatmap_id))
    list_of_params.append(parameterize_id("u", user_id))
    list_of_params.append(parameterize_mode(mode))

    ## Build the full request URL and return the response.
    return urllib.request.urlopen(build_request(list_of_params, "https://osu.ppy.sh/api/get_scores?")).read()


## get_user - Returns a JSON payload containing information about a beatmap set or beatmap.
## key        - Your API key. (Required)
## user_id    - A user ID. (Required)
## mode       - The game mode for which to get info.
##                  (0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania, Default = 0)
## type       - Specifies rather the user_id specified is an ID or a username.
##                  (id = id, string = username, default = Autodetect)
## event_days - Maximum number of days between now and last event date.
##                  (1 - 31, default = 1)
def get_user(key, user_id, mode, type, event_days):
    ## Create a list to store the attributes which are present.
    list_of_params = []

    ## Populate the list of PHP variables.
    ## Only prepend the PHP variable names if they are there.
    list_of_params.append(parameterize_key(key))
    list_of_params.append(parameterize_id("u", user_id))
    list_of_params.append(parameterize_mode(mode))
    list_of_params.append(parameterize_type(type))
    list_of_params.append(parameterize_event_days(event_days))

    ## Build the request URL and return the response.
    return urllib.request.urlopen(build_request(list_of_params, "https://osu.ppy.sh/api/get_user?")).read()


## get_user_best - Returns the top scores for the specified user.
## key           - Your API key. (Required)
## user_id       - A user ID. (Required)
## mode          - The game mode for which to get info.
##                     (0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania, Default = 0)
## limit         - # of results to return.
##                     (1 - 50, Default = 10).
## type          - Specifies rather the user_id specified is an ID or a username.
##                     (id = id, string = username, default = Autodetect)
def get_user_best(key, user_id, mode, limit, type):
    ## Create a list to store the attributes which are present.
    list_of_params = []

    ## Populate the list of PHP variables.
    ## Only prepend the PHP variable names if they are there.
    list_of_params.append(parameterize_key(key))
    list_of_params.append(parameterize_id("u", user_id))
    list_of_params.append(parameterize_mode(mode))
    list_of_params.append(parameterize_limit(limit))
    list_of_params.append(parameterize_type(type))

    ## Build the full request URL and return the response.
    return urllib.request.urlopen(build_request(list_of_params, "https://osu.ppy.sh/api/get_user_best?")).read()


## get_user_recent - Returns the user's ten most recent plays.
## key             - Your API key. (Required)
## user_id         - A user ID. (Required)
## mode            - The game mode for which to get info.
##                       (0 = osu!, 1 = Taiko, 2 = CtB, 3 = osu!mania, Default = 0)
## type            - Specifies rather the user_id specified is an ID or a username.
##                       (id = id, string = username, default = Autodetect)
def get_user_recent(key, user_id, mode, type):
    ## Create a list to store the attributes which are present.
    list_of_params = []

    ## Populate the list of PHP variables.
    ## Only prepend the PHP variable names if they are there.
    list_of_params.append(parameterize_key(key))
    list_of_params.append(parameterize_id("u", user_id))
    list_of_params.append(parameterize_mode(mode))
    list_of_params.append(parameterize_type(type))

    ## Build the full request URL and return the response.
    return urllib.request.urlopen(build_request(list_of_params, "https://osu.ppy.sh/api/get_user_recent?")).read()


## parameterize_event_days - Formats event days as a PHP parameter.
def parameterize_event_days(event_days):
    if (event_days == ""):
        event_days = "event_days=1"
    elif (int(event_days) >= 1 and int(event_days) <= 31):
        event_days = "event_days=" + str(event_days)
    else:
        print("    Invalid event_days \"" + str(event_days) + ".\"")
        sys.exit()

    return event_days


## parameterize_id - Formats an ID as a PHP parameter.
## t               - The type of ID.
##                       (b = beatmap, s = beatmap set, u = user)
## id              - A beatmap, beatmap set, or user ID.
def parameterize_id(t, id):
    if (t != "b" and t != "s" and t != "u" and t != "mp"):
        print("    Invalid type \"" + str(t) + ".\"")
        sys.exit()

    if (len(str(id)) != 0):
        return t + "=" + str(id)
    else:
        return ""


## parameterize_key - Formats an API key as a PHP parameter.
## key              - An API key.
def parameterize_key(key):
    if (len(key) == 40):
        return "k=" + key
    else:
        print("    Invalid key \"" + str(key) + ".\"")
        sys.exit()


## parameterize_limit - Formats the limit as a PHP parameter.
## limit              - The maximum # of scores to show.
def parameterize_limit(limit):
    ## Default case: 10 scores
    if (limit == ""):
        limit = "limit=10"
    elif (int(limit) >= 1 and int(limit) <= 50):
        limit = "limit=" + str(limit)
    else:
        print("    Invalid limit \"" + str(limit) + ".\"")
        sys.exit()

    return limit


## parameterize_mode - Formats a mode as a PHP parameter.
## mode              - The game mode for which to get info.
def parameterize_mode(mode):
    ## Default case: 0 (osu!)
    if (mode == ""):
        mode = "m=0"
    elif (int(mode) >= 0 and int(mode) <= 3):
        mode = "m=" + str(mode)
    else:
        print("    Invalid mode \"" + str(mode) + ".\"")
        sys.exit()

    return mode


## parameterize_since - Formats a since as a PHP parameter.
## since              - A MYSQL-formatted date which is the cut off for the time period in which to return data.
def parameterize_since(since):
    if (since == ""):
        return since
    if (re.match("[0-9]{4}\-[0-1]?[1-9]\-[0-3]?[1-9] [0-2]?[0-9]\:[0-5][0-9]\:[0-5][0-9]", since)):
        return "since=" + str(since)
    else:
        print("    Invalid since \"" + str(since) + ".\"")
        sys.exit()


## parameterize_type - Formats a type as a PHP parameter.
## type              - Specifies rather the user_id specified is an ID or a username.
def parameterize_type(type):
    if (type == ""):
        return type
    elif (type == "id" or type == "string"):
        return "type=" + str(type)
    else:
        print("    Invalid type \"" + str(type) + ".\"")
        sys.exit()

        ## End of classless methods.
