import requests
from bs4 import BeautifulSoup


def get(group):
    meetup = {}
    url = "https://api.meetup.com/{}/events/?status=upcoming&page=1&desc=True".format(group)
    headers = {
                "Content-Type": "application/json"
              }
    response = requests.request("GET", url, headers=headers)
    ''' If API isn't responding continue to next module '''
    if response.status_code != 200:
        meetup["url"] = False
        meetup["error"] = "{} {}".format(
            response.status_code, response.text
            )
        return meetup
    item = response.json()

    if len(item) == 0:
        meetup["url"] = False
        meetup["error"] = "{}: {}".format(
            response.status_code, "no upcoming events"
            )
        return meetup

    meetup["title"] = item[0]["name"]
    meetup["url"] = item[0]["link"]
    meetup["venue"] = item[0]["venue"]["address_1"]+", "+item[0]["venue"]["city"]
    meetup["avatar"] = meetupAvatar(group)
    if len(item[0]["description"]) > 200:
        soup = BeautifulSoup(item[0]["description"][0:200], 'html.parser')
        meetup["desc"] = soup.getText()+"..."
    else:
        soup = BeautifulSoup(item[0]["description"], 'html.parser')
        meetup["desc"] = soup.getText()
    meetup["date"] = item[0]["local_date"]+" "+item[0]["local_time"]
    return meetup


def meetupAvatar(group):
    url = "https://api.meetup.com/{}?&sign=true&photo-host=public".format(group)
    headers = {
                "Content-Type": "application/json"
              }
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        avatar = "https://www.meetup.com/mu_static/en-US/logo--mSwarm--2color.4ff7188b.svg"
        return avatar
    try:
        item = response.json()
        avatar = item["key_photo"]["photo_link"]
    except Exception:
        avatar = "https://www.meetup.com/mu_static/en-US/logo--mSwarm--2color.4ff7188b.svg"
    return avatar
