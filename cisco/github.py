import requests


def get(org):
    repo = {}
    url = "https://api.github.com/orgs/{}/repos?sort=created&per_page=1".format(org)
    headers = {
                "Content-Type": "application/json"
              }
    response = requests.request("GET", url, headers=headers)
    ''' If API isn't responding continue to next module '''
    if response.status_code != 200:
        repo["url"] = False
        repo["error"] = "{} {}".format(response.status_code, response.text)
        return repo
    item = response.json()
    
    repo["title"] = item[0]["full_name"]
    repo["url"] = item[0]["html_url"]
    if item[0]["language"] is None:
        repo["language"] = "Not available"
    else:
        repo["language"] = item[0]["language"]
    repo["avatar"] = item[0]["owner"]["avatar_url"]
    if item[0]["description"] is None:
        repo["desc"] = "No description, website, or topics provided."
    else:
        if len(item[0]["description"]) > 200:
            repo["desc"] = item[0]["description"][0:200]+"..."
        else:
            repo["desc"] = item[0]["description"]
    repo["date"] = item[0]["created_at"]

    return repo
