# Cisco DevNet community Webex bot

Cisco Webex Teams Bot that fetches the latest from blog, github and meetup.
Runs every hour (default) and stores the latest URL also in a database.

## Demo

![](demo-webexteams.gif)
#### Python script
![](demo-script.gif)

## Features

Modules supported

- Cisco DevNet Blog
  - https://blogs.cisco.com/developer
- Github Orgs
  - https://api.github.com/orgs/
- Meetup
  - https://api.meetup.com/

Database used

- AWS DynamoDB
  - Cloud
    - https://aws.amazon.com/dynamodb/
  - Local Dev / Private Cloud
    - https://hub.docker.com/r/amazon/dynamodb-local/

## default config
_(for the modules)_

```
# Enable modules to fetch data and create Webex Adaptive Cards
# Comment module if you want to disable a module
modules:
    # URL to Cisco DevNet blog
    blog:
      - https://blogs.cisco.com/developer
    # Github.com org name
    github:
        orgs:
          - ciscodevnet
    # BrightTALK
    brighttalk:
      - 17628
    # Meetup group name
    meetup:
      - cisco-developers-club-stockholm
```
If you want to edit these URLs, for the modules.  
Then clone this repo and edit ```config.yaml```

## Technologies & Frameworks Used

**Cisco Products & Services:**

- Cisco Webex Teams

**Third-Party Products & Services:**

- REST API
  - Github
  - Meetup
  - BrightTALK

**Tools & Frameworks:**

- python
- docker
- webexteamssdk

## Installation

### Prerequisites
* AWS DynamoDB
  * https://aws.amazon.com/dynamodb/
  * Local
    * https://hub.docker.com/r/amazon/dynamodb-local/
      * with UIs
        * https://hub.docker.com/r/aaronshaf/dynamodb-admin
        * https://hub.docker.com/r/boogak/dynamodb-admin

You can create the DynamoDB Table with ```--init``` flag

* Database structure
```
{
    "AttributeName": "type",
    "KeyType": "HASH"
},
{
    "AttributeName": "link",
    "KeyType": "RANGE"
}
```

### docker

###### Start service
```
docker run -d \
-e AWS_ACCESS_KEY_ID=changeme \
-e AWS_SECRET_ACCESS_KEY=changeme \
-e AWS_DEFAULT_REGION=eu-north-1 \
-e WEBEX_TEAMS_ACCESS_TOKEN=changeme \
-e WEBEX_TEAMS_ROOM_ID=changeme \
robertcsapo/cisco-devnet-sweden-community-webex-bot
```

###### OS Environment and help section

```
usage: run.py [-h] [--config CONFIG] [--table TABLE] [--init] [--delay DELAY] [--force] [--dry] [--debug] [--version]

Cisco DevNet community Webex bot

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  Read different config file (default: config.yaml)
  --table TABLE    AWS DynamoDB Table (default: cisco-devnet-webex-bot)
  --init           Initialize database (default: False)
  --delay DELAY    Change delay in seconds (default: 3600)
  --force          Force update on latest from modules (default: False)
  --dry            Dry-run doesn't post anything to Webex (default: False)
  --debug          Display OS/ARGs settings (default: False)
  --version        show program's version number and exit
```

###### Example
```
docker run -it --rm robertcsapo/cisco-devnet-sweden-community-webex-bot --config config.yaml --debug
```

### docker-compose

###### Clone the repo
```
git clone https://github.com/robertcsapo/cisco-devnet-community-webex-bot
```

###### Edit config.yaml
```
vim config.yaml
```

###### Start service (cloud image)
```
docker-compose -f docker-compose.yaml up
```

###### Start service (local image build)
```
docker-compose -f docker-compose-build.yaml up
```

## Customization

### Cisco Webex Teams Adaptive Card

Warning!

Changing the Cisco Webex Teams Adaptive Card template could cause this script to not work properly.

#### Design

You can design your own Adaptive Cards, to be used with Cisco Webex Teams [here](https://developer.webex.com/buttons-and-cards-designer)  
_(More details about how adaptive cards works can be found [here](https://docs.microsoft.com/en-us/adaptive-cards/))_

#### Edit the source code

Replace your own designed adaptive card in the ```card.json``` file.  
Then you need to match all the data objects in the ```cisco/webex.py``` file.  

```
    ''' Read in Adaptive Card template '''
    with open('card.json') as file:
        data = json.load(file)

    ''' Below changes the data on Adaptive Card Template '''
```

Edit from here

```
''' Avatar Image URL for Card '''
data["content"]["body"][0]["columns"][0]["items"][0]["url"] = value["avatar"]
```
...   
Stop editing here
```
''' ActionURL for Card '''
data["content"]["body"][3]["actions"][0]["url"] = value["url"]
```
Save the ```cisco/webex.py``` file. 

#### Build with local changes
[Local image build](#start-service-local-image-build)

## Authors & Maintainers

Smart people responsible for the creation and maintenance of this project:

- Robert Csapo <rcsapo@cisco.com>

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
