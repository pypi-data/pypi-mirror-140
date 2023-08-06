import datetime
import logging
import json
import os
import http.client
from urllib.parse import urlparse


def date_time_now():
    to_return = datetime.datetime.utcnow().isoformat()
    return to_return


def display(message):
    logging.log(level=1, msg=message)
    # to_print = f"{date_time_now()}\t{message}"
    to_print = f'{message}'
    print(to_print)
    return True


def get_path():
    default_path = str(os.getcwd())
    display(message=default_path)
    return default_path


def config_reader():
    with open(file=get_path() + "gaze.config.json", mode='r') as cf:
        gaze_config = json.load(cf)
        return gaze_config


def send_message_to_slack(message):
    slack_config = config_reader().get("slack")
    slack_url = urlparse(slack_config.get("ecs-cluster-alert").get("hook"))

    conn = http.client.HTTPSConnection(slack_url.netloc)

    the_data = {
        "channel": slack_config.get("ecs-cluster-alert").get("channel"),
        "text": message
    }

    headers = {'Content-Type': "application/json"}

    conn.request("POST", slack_url.path, json.dumps(the_data), headers)

    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")
