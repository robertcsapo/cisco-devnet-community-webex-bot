from webexteamssdk import WebexTeamsAPI
import os
import json
import yaml


def card(type, value, args):
    result = {}
    ''' Read settings from ENV or Config file '''
    settings = config(args)
    try:
        api = WebexTeamsAPI(access_token=settings["WEBEX_TEAMS_ACCESS_TOKEN"])
    except Exception as e:
        raise Exception("ERROR: Problem with API for Cisco Webex Teams - {}".format(e))
        result["state"] = "error"
        return result
    ''' Read in Adaptive Card template '''
    with open('card.json') as file:
        data = json.load(file)

    ''' Below changes the data on Adaptive Card Template '''

    ''' Avatar Image URL for Card '''
    data["content"]["body"][0]["columns"][0]["items"][0]["url"] = value["avatar"]
    ''' Title for Card '''
    data["content"]["body"][0]["columns"][1]["items"][0]["text"] = value["title"]
    ''' Date for Card '''
    data["content"]["body"][0]["columns"][1]["items"][1]["text"] = value["date"]
    ''' Description for Card '''
    data["content"]["body"][1]["text"] = value["desc"]
    ''' Description for Card '''
    if type == "blog":
        data["content"]["body"][2]["facts"][0]["title"] = "Author  "+u'\U0001F58C'
        data["content"]["body"][2]["facts"][0]["value"] = value["author"]
    elif type == "github":
        data["content"]["body"][2]["facts"][0]["title"] = "Language  "+u'\U0001F9D1\U0000200D\U0001F4BB'
        data["content"]["body"][2]["facts"][0]["value"] = value["language"]
    elif type == "brighttalk":
        data["content"]["body"][2]["facts"][0]["title"] = "Categories  "+u'\U0001F3F7'
        data["content"]["body"][2]["facts"][0]["value"] = value["categories"]
    elif type == "meetup":
        data["content"]["body"][2]["facts"][0]["title"] = "Location  "+u'\U0001F3E2'
        data["content"]["body"][2]["facts"][0]["value"] = value["venue"]
    ''' ActionURL for Card '''
    data["content"]["body"][3]["actions"][0]["url"] = value["url"]

    ''' Send the Adaptive Card as attachments '''
    if args.dry is False:
        try:
            api.messages.create(
                                settings["WEBEX_TEAMS_ROOM_ID"],
                                text="Title: {} - URL: {}".format(value["title"], value["url"]),
                                attachments=[{
                                    "contentType": "application/vnd.microsoft.card.adaptive",
                                    "content": data["content"]
                                    }],
                                )
        except Exception as e:
            raise Exception("ERROR: Couldn't post to Cisco Webex Teams - {}".format(e))
            result["state"] = "error"
            return result
    else:
        ''' JSON dump Adaptive Card '''
        result["state"] = "dry-run"
        result["data"] = data
        return result

    if args.force is True:
        result["state"] = "force"
    else:
        result["state"] = "new"
    return result


def config(args):
    result = {}
    ''' ENV has higher prio then config file '''
    try:
        os.environ["WEBEX_TEAMS_ACCESS_TOKEN"]
        os.environ["WEBEX_TEAMS_ROOM_ID"]
        result["WEBEX_TEAMS_ACCESS_TOKEN"] = os.environ["WEBEX_TEAMS_ACCESS_TOKEN"]
        result["WEBEX_TEAMS_ROOM_ID"] = os.environ["WEBEX_TEAMS_ROOM_ID"]
    except KeyError:
        ''' Open config file '''
        with open(args.config, "r") as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
        if (config["webex"]["WEBEX_TEAMS_ACCESS_TOKEN"] is not None and
                config["webex"]["WEBEX_TEAMS_ROOM_ID"] is not None):
            result["WEBEX_TEAMS_ACCESS_TOKEN"] = config["webex"]["WEBEX_TEAMS_ACCESS_TOKEN"]
            result["WEBEX_TEAMS_ROOM_ID"] = config["webex"]["WEBEX_TEAMS_ROOM_ID"]
            os.environ["WEBEX_TEAMS_ACCESS_TOKEN"] = config["webex"]["WEBEX_TEAMS_ACCESS_TOKEN"]
            os.environ["WEBEX_TEAMS_ROOM_ID"] = config["webex"]["WEBEX_TEAMS_ROOM_ID"]
            return result
        else:
            raise Exception("WEBEX_TEAMS_ACCESS_TOKEN/WEBEX_TEAMS_ROOM_ID missing")
            return

    return result
