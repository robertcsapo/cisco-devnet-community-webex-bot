import requests
import xmltodict
from datetime import datetime
from bs4 import BeautifulSoup


def get(id):
    result = {}
    url = "https://www.brighttalk.com/channel/{}/feed?size=1".format(id)
    headers = {
                "Content-Type": "application/xml"
              }
    response = requests.request("GET", url, headers=headers)

    ''' If API isn't responding continue to next module '''
    if response.status_code != 200:
        result["url"] = False
        result["error"] = "{} {}".format(response.status_code, response.text)
        return result
    try:
        item = xmltodict.parse(response.text)
    except Exception:
        result["url"] = False
        result["error"] = "{}: {}".format(response.status_code, response.text)
        return result

    result["title"] = item["feed"]["entry"]["title"]
    result["author"] = item["feed"]["entry"]["author"]["name"]
    result["url"] = item["feed"]["entry"]["link"][0]["@href"]
    result["categories"] = ""
    try:
        for category in item["feed"]["entry"]["category"]:
            result["categories"] = result["categories"]+category["@term"]+" "
        result["categories"] = result["categories"][0:-1]
    except Exception:
        result["categories"] = "Not available"
    result["avatar"] = "https://www.brighttalk.com/communication/396682/thumbnail1587132190409.png"
    if len(item["feed"]["entry"]["summary"]) > 200:
        soup = BeautifulSoup(item["feed"]["entry"]["summary"][0:200], 'html.parser')
        result["desc"] = soup.getText()+"..."
    else:
        soup = BeautifulSoup(item["feed"]["entry"]["summary"], 'html.parser')
        result["desc"] = soup.getText()
    result["date"] = int(item["feed"]["entry"]["bt:start"])
    dateObj = datetime.fromtimestamp(result["date"])
    result["date"] = dateObj.strftime("%Y-%m-%d %H:%M")
    return result

''' TODO REMOVE '''
if __name__ == "__main__":
    import sys
    id = "17628"
    test = get(id)
    import json
    test = json.dumps(test, indent=4)
    print(test)
