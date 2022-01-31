import os
import sys
import datetime
import json
import requests
import urllib.parse
from greynoise import GreyNoise

# grab whatever query we want
INFILE = sys.argv[1]
GNQL = open(INFILE, 'r').read()
GNQL_ENCODED = urllib.parse.quote(GNQL)

# get os env vars
GREYNOISE_API_KEY = os.environ.get('GREYNOISE_API_KEY')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

# init GreyNoise sdk
session = GreyNoise(api_key=GREYNOISE_API_KEY, integration_name="ThreatDudes-DiscordAlert")

# whats the time?
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

try:
    # try getting greynoise data
    results = session.stats(GNQL)
except Exception as e:
    print(f'[!] Error making request to GreyNoise: {e}')
    exit

# FUNCTIONS


# function: formatData
# formats input dict to make string message
def formatData(obj: list, name: str):
    msg = f'**{name}**\n'
    msg += '```\n'
    name = name.lower().replace(" ", "_")
    key_list = [entry[name] for entry in obj[:10]]
    count_list = [entry["count"] for entry in obj[:10]]
    i = 0
    while i < len(key_list):
        msg += f'{list(key_list)[i]:48}{list(count_list)[i]}\n'
        i += 1
    msg += '```\n'
    return msg


# function: postToWebhook
# posts message content to webhook
def postToWebhook(webhook_url: str, msg: str):

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'content': msg
    }

    response = requests.post(webhook_url, data=json.dumps(data), headers=headers)

# PARSING


try:
    classification = results["stats"]["classifications"]
    country = results["stats"]["countries"]
    organization = results["stats"]["organizations"]
    operatingsystem = results["stats"]["operating_systems"]
    tags = results["stats"]["tags"]

    message = '**GreyNoise Automated Report**\n'
    message += f'Time: {timestamp}\n'
    message += f'Query: {GNQL}\n'
    message += f'Results: {results["count"]}\n'
    message += '---------------------\n'
    message += formatData(classification, 'Classification')
    message += formatData(country, 'Country')
    message += formatData(organization, 'Organization')
    message += formatData(operatingsystem, 'Operating System')
    message += formatData(tags, 'Tag')
    message += f'More at `https://www.greynoise.io/viz/query/?gnql={GNQL_ENCODED}`\n'
except Exception as e:
    print(f'[!] Error parsing data for report: {e}')
    exit

# POSTING
try:
    postToWebhook(DISCORD_WEBHOOK_URL, message)

except Exception as e:
    print(f'[!] Error issue posting to Discord: {e}')
    exit
