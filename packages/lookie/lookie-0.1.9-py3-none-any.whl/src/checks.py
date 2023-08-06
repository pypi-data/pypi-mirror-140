import http.client
import os
import subprocess
import time
import urllib.request
from urllib.parse import urlparse
from src.utilities import display


def check_ping(hostname):
    """Check ping response of a host or IP."""
    res = subprocess.call(['ping', '-c', '1', '-W', '1000', hostname], stdout=open(os.devnull, 'wb'))
    if res == 0:
        """Ping ok"""
        return 1
    else:
        return 0


def ping_test(args):
    threshold = 80

    hostname = args.hostname
    surname = args.surname
    how_many_check = args.count
    interval = args.interval

    counter = 0

    for _ in range(how_many_check):
        ping_response = check_ping(hostname=hostname)
        counter += ping_response
        time.sleep(interval)

    percentage = int((counter / how_many_check) * 100)

    if percentage < threshold:
        message = f"Ping check failed at '{surname}: {hostname}'."
        display(message=message)
    else:
        message = f"Ping check passed at '{surname}: {hostname}'."
        display(message=message)


def string_check(args):
    url = args.url
    string = args.string
    message = f"Found '{string}' at {url}"

    req = urllib.request.Request(url)
    req.add_header(
        'User-Agent',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36')
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        if string.lower() in the_page.decode("utf-8").lower():
            display(message=message)
            return True
        else:
            display(message=message.replace("Found", "Not Found"))
            return False


def string_checka(args):
    url = args.url
    string = args.string

    parsed_url = urlparse(url=url)

    domain = parsed_url.netloc
    scheme = parsed_url.scheme
    path = parsed_url.path

    if "https" in scheme.lower():
        conn = http.client.HTTPSConnection(domain)
    else:
        conn = http.client.HTTPConnection(domain)

    payload = ""

    headers = {
        'Content-Type': "application/json",
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }

    conn.request("GET", path, payload, headers=headers)

    res = conn.getresponse()

    message = f"Found '{string}' at {url}"

    if res.status == 200:
        data = res.read()
        if string.lower() in data.decode("utf-8").lower():
            display(message=message)
            return True
        else:
            display(message=message.replace("Found", "Not Found"))
            return False
    else:
        message = f"Error accessing {url}"
        display(display(message=message))
        return False