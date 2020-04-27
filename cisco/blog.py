import requests
from bs4 import BeautifulSoup


def get(link):
    post = {}
    url = requests.get(link)
    ''' If API isn't responding continue to next module '''
    if url.status_code != 200:
        post["url"] = False
        post["error"] = "{} {}".format(url.status_code, "html parsing")
        return post
    soup = BeautifulSoup(url.content, "html.parser")
    for item in soup.find_all("a", class_="card-link"):
        title = item.getText()
        url = item.get("href")
        post["title"] = title[1:-1]
        post["url"] = url
        post["author"] = postAuthor(soup)
        post["avatar"] = postAvatar(url)
        post["desc"] = postDesc(soup)
        post["date"] = postDate(soup)
        return post


def postAuthor(soup):
    for item in soup.find_all("a", rel="author"):
        value = item.getText()
        return value


def postDesc(soup):
    for item in soup.find_all("p", class_="card-paragraph"):
        value = item.getText()
        value = value.strip("\n\t")
        if len(value) > 200:
            value = value[0:200]+"..."
        else:
            value
        return value


def postDate(soup):
    ''' Get the date from the blog article '''
    for item in soup.find_all("p", class_="card-social-header-date"):
        value = item.getText()
        value = value.strip("\n\t ")
        return value


def postAvatar(url):
    ''' Easier to fetch Avatar directly fron blogpost '''
    url = requests.get(url)
    url.raise_for_status()
    soup = BeautifulSoup(url.content, "html.parser")
    for item in soup.find_all("img", class_="avatar"):
        value = item.get("src")
        return value
