import boto3
import os
import time
import yaml


def latest(table, type, link, args):
    result = {}
    settings = config(args)
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=os.environ["AWS_DEFAULT_REGION"],
        endpoint_url=settings["AWS_ENDPOINT_URL"]
        )
    table = dynamodb.Table(table)
    ''' Trying to find unique URL in DynamoDB '''
    try:
        response = table.get_item(
                                Key={
                                    "link": link,
                                    "type": type
                                    }
                                )
    except Exception as e:
        raise Exception("ERROR: Problem reading DynamoDB - {}".format(e))
    ''' If there's no Item, then it's new entry '''
    try:
        response["Item"]
    except KeyError:
        ''' Return false, as Empty response '''
        result["link"] = False
        return result
    result["link"] = response["Item"]["link"]
    return result


def add(table, type, title, link, args):
    timestamp = int(time.time())
    settings = config(args)
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=os.environ["AWS_DEFAULT_REGION"],
        endpoint_url=settings["AWS_ENDPOINT_URL"]
        )
    table = dynamodb.Table(table)
    try:
        table.put_item(
                        Item={
                           "title": title,
                           "link": link,
                           "type": type,
                           "timestamp": str(timestamp),
                           }
                      )
    except Exception as e:
        raise Exception("ERROR: Problem updating DynamoDB - {}".format(e))

    return


def dbInit(table, args):
    result = {}
    settings = config(args)
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=os.environ["AWS_DEFAULT_REGION"],
        endpoint_url=settings["AWS_ENDPOINT_URL"]
        )
    ''' Create DynamoDB Database '''
    try:
        dynamodb.create_table(
                TableName=table,
                KeySchema=[
                    {
                        "AttributeName": "type",
                        "KeyType": "HASH"
                    },
                    {
                        "AttributeName": "link",
                        "KeyType": "RANGE"
                    }
                ],
                AttributeDefinitions=[
                    {
                        "AttributeName": "type",
                        "AttributeType": "S"
                    },
                    {
                        "AttributeName": "link",
                        "AttributeType": "S"
                    },

                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 2,
                    "WriteCapacityUnits": 2
                }
            )
    except Exception as e:
        raise Exception("ERROR: {}".format(e))

    result["success"] = True
    return result


def config(args):
    result = {}
    ''' Open config file '''
    with open(args.config, "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    ''' ENV has higher prio then config file '''
    try:
        os.environ["AWS_ACCESS_KEY_ID"]
        os.environ["AWS_SECRET_ACCESS_KEY"]
        result["AWS_ACCESS_KEY_ID"] = os.environ["AWS_ACCESS_KEY_ID"]
        result["AWS_SECRET_ACCESS_KEY"] = os.environ["AWS_SECRET_ACCESS_KEY"]
    except KeyError:
        if (config["dynamodb"]["AWS_ACCESS_KEY_ID"] is not None and
                config["dynamodb"]["AWS_SECRET_ACCESS_KEY"] is not None):
            result["AWS_ACCESS_KEY_ID"] = config["dynamodb"]["AWS_ACCESS_KEY_ID"]
            result["AWS_SECRET_ACCESS_KEY"] = config["dynamodb"]["AWS_SECRET_ACCESS_KEY"]
            os.environ["AWS_ACCESS_KEY_ID"] = config["dynamodb"]["AWS_ACCESS_KEY_ID"]
            os.environ["AWS_SECRET_ACCESS_KEY"] = config["dynamodb"]["AWS_SECRET_ACCESS_KEY"]
        else:
            raise Exception("AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY missing")
            return
    try:
        os.environ["AWS_DEFAULT_REGION"]
        result["AWS_DEFAULT_REGION"] = os.environ["AWS_DEFAULT_REGION"]
    except KeyError:
        try:
            config["dynamodb"]["AWS_DEFAULT_REGION"]
            if (config["dynamodb"]["AWS_DEFAULT_REGION"] is not None):
                os.environ["AWS_DEFAULT_REGION"] = config["dynamodb"]["AWS_DEFAULT_REGION"]
                result["AWS_DEFAULT_REGION"] = os.environ["AWS_DEFAULT_REGION"]
        except KeyError:
            raise Exception("AWS Region missing in config")

    try:
        os.environ["AWS_ENDPOINT_URL"]
        result["AWS_ENDPOINT_URL"] = os.environ["AWS_ENDPOINT_URL"]
    except KeyError:
        try:
            config["dynamodb"]["AWS_ENDPOINT_URL"]
            if (config["dynamodb"]["AWS_ENDPOINT_URL"] is not None):
                os.environ["AWS_ENDPOINT_URL"] = config["dynamodb"]["AWS_ENDPOINT_URL"]
                result["AWS_ENDPOINT_URL"] = config["dynamodb"]["AWS_ENDPOINT_URL"]
            else:
                result["AWS_ENDPOINT_URL"] = None
        except KeyError:
            result["AWS_ENDPOINT_URL"] = None
            pass

    return result
