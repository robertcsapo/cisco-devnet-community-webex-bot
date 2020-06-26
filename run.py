"""Cisco DevNet community Webex bot Console Script.

Copyright (c) 2018 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Robert Csapo"
__email__ = "rcsapo@cisco.com"
__version__ = "0.2"
__copyright__ = "Copyright (c) 2018 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"
__app__ = "cisco-devnet-community-webex-bot"

import time
import yaml
import os
import argparse
import logging
from aws import dynamodb
from cisco import blog
from cisco import github
from cisco import brighttalk
from cisco import meetup
from cisco import webex


def collector(type, args, config):
    ''' Fetch latest of the type '''
    ''' Reads data for types in config file '''
    if type == "blog":
        items = blog.get(config["modules"]["blog"][0])
    elif type == "github":
        items = github.get(config["modules"]["github"]["orgs"][0])
    elif type == "brighttalk":
        items = brighttalk.get(config["modules"]["brighttalk"][0])
    elif type == "meetup":
        items = meetup.get(config["modules"]["meetup"][0])
    if args.debug is True:
        logging.info("DEBUG: {} module - {}".format(
            type,
            items
            )
        )

    if args.debug is True:
        logging.info("DEBUG: {} module - {}".format(
            type,
            items
            )
        )

    ''' If it wasn't possible to get new data from modules API '''
    ''' Then continue to next module '''
    if items["url"] is False:
        logging.error("Problem with {} API - {}".format(
            type,
            items["error"]
            )
        )
        return

    ''' Check if link/url exist in db for that type '''
    latest = dynamodb.latest(args.table, type, items["url"], args)
    if args.debug is True:
        logging.info("DEBUG: dynamodb - {}".format(
            items
            )
        )

    ''' Match unique links of the type '''
    if (
        (latest["link"] is False or latest["link"] != items["url"])
        and args.dry is False
            ):
        ''' Post to Webex Teams if new unique link '''
        dynamodb.add(args.table, type, items["title"], items["url"], args)
        status = webex.card(type, items, args)
        logging.info("Status: {} - {} - {}".format(
            status["state"],
            type,
            items["url"]
            )
        )
        return
    else:
        if args.force is True:
            ''' Force updates to Webex Teams '''
            status = webex.card(type, items, args)
            logging.info("Status: {} - {} - {}".format(
                status["state"],
                type,
                items["url"]
                )
            )
        elif args.dry is True:
            ''' Don't post anything to Webex Teams '''
            status = webex.card(type, items, args)
            logging.warning("Status: {} - {} (not posting to webex) - {}".format(
                status["state"],
                type,
                items["url"]
                )
            )
            logging.info("Adaptive Card Data: {}".format(
                status["data"]
                )
            )
        else:
            logging.info("Up-to-date {}".format(
                type
                )
            )
        return


if __name__ == "__main__":
    ''' Logging module '''
    logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser(
        description="Cisco DevNet community Webex bot",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument("--config", default="config.yaml",
                        help="Read different config file")
    parser.add_argument("--table", default="cisco-devnet-community-webex-bot",
                        help="AWS DynamoDB Table")
    parser.add_argument("--init", action="store_true",
                        help="Initialize database")
    parser.add_argument("--delay", type=int, default=3600,
                        help="Change delay in seconds")
    parser.add_argument("--force", action="store_true",
                        help="Force update on latest from modules")
    parser.add_argument("--dry", action="store_true",
                        help="Dry-run doesn't post anything to Webex")
    parser.add_argument("--debug", action="store_true",
                        help="Display OS/ARGs settings")
    parser.add_argument("--version", action="version",
                        version=__app__+" v"+__version__)

    args = parser.parse_args()

    ''' Debug is enabled '''
    if args.debug is True:
        logging.info("DEBUG: {}".format(
            os.environ
            )
        )
        logging.info("DEBUG: {}".format(
            args
            )
        )

    while True:

        ''' Initializing Database '''
        if args.init is True:
            dbInit = dynamodb.dbInit(args.table, args)
            if dbInit["success"] is True:
                args.init = False
                logging.info(
                    "SUCCESS: Created DynamoDB - {}".format(
                        args.table
                        )
                    )
            else:
                raise Exception("ERROR: Unknown error")

        ''' Enable modules from config file '''
        with open(args.config, "r") as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
        ''' Loop through modules and create Cisco Webex Adaptive Cards '''
        for type in config["modules"]:
            collector(type, args, config)

        if (args.force is True or args.dry is True):
            logging.warning("Force or Dry flag is set as True. Stopping...")
            break

        ''' Sleep before running script again '''
        logging.info("Sleep for {} seconds".format(
            args.delay
            )
        )
        time.sleep(args.delay)
