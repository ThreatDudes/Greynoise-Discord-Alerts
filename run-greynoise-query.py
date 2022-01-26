import os
import sys
import datetime
import json
import requests
import urllib.parse
from collections import Counter

# grab whatever query we want
INFILE = sys.argv[1]
GNQL = open(INFILE,'r').read()
GNQL_ENCODED = urllib.parse.quote(GNQL)

# get os env vars
GREYNOISE_API_KEY = os.environ.get('GREYNOISE_API_KEY')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

# init greynoise url with gnql query
URL = f'https://api.greynoise.io/v2/experimental/gnql?query={GNQL_ENCODED}&size=10000'

# init headers for greynoise request
headers = {
    'Accept': 'application/json',
    'key': GREYNOISE_API_KEY
}

# whats the time? 
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

try:
    # try getting greynoise data
    response = requests.get(URL, headers=headers)
    data = response.json()
    results = data['data']
except Exception as e:
    print(f'[!] Error making request to Greynoise: {e}')
    exit

# FUNCTIONS

# function: dictToSortedList
# gets a dict and sorts to list
def dictToSortedList(obj: dict):
    obj2 = []
    for k in obj.keys():
        obj2.append({'k':k,'v':obj[k]})
    return sorted(obj2, key=lambda k : k['v'], reverse=True)

# function: sortedListToDict
# takes a sorted lists and dicts it
def sortedListToDict(obj: list):
    return [{row['k']:row['v']} for row in obj]

# function: dictTop10
# top ten dict entries
def dictTop10(obj: dict):
    return dict(list(obj.items())[:10])

# function: listTop10
# top ten list entries
def listTop10(obj: dict):
    return obj[:10]

# function: transform
# complete transformation chain
def transform(obj: dict):
    return sortedListToDict(listTop10(dictToSortedList(obj)))

# function: formatData
# formats input dict to make string message
def formatData(obj: list, name: str):
    msg = f'**{name}**\n'
    msg += f'```\n'
    for entry in obj:
        msg += f'{list(entry.keys())[0]:32}{list(entry.values())[0]}\n'
    msg += f'```\n'
    return msg

# function: postToWebhook
# posts message content to webhook
def postToWebhook(webhook_url: str,msg: str):

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'content': msg
    }

    response = requests.post(webhook_url,data=json.dumps(data),headers=headers)

# PARSING

try:
    classification = transform(dict(Counter([x['classification'] for x in results])))
    country = transform(dict(Counter([x['metadata']['country'] for x in results if 'country' in x['metadata'].keys()])))
    organization = transform(dict(Counter([x['metadata']['organization'] for x in results if 'organization' in x['metadata'].keys()])))
    operatingsystem = transform(dict(Counter([x['metadata']['os'] for x in results if 'os' in x['metadata'].keys()])))
    tags = transform(dict(Counter([tag for x in [x['tags'] for x in results] for tag in x])))

    message = f'**GreyNoise Automated Report**\n'
    message += f'Time: {timestamp}\n'
    message += f'Query: {GNQL}\n'
    message += f'Results: {len(results)}\n'
    message += f'---------------------\n'
    message += formatData(classification,'Classification')
    message += formatData(country,'Country')
    message += formatData(organization,'ISP')
    message += formatData(operatingsystem,'OS')
    message += formatData(tags,'Tags')
    message += f'More at `https://www.greynoise.io/viz/query/?gnql={GNQL_ENCODED}`\n'
except Exception as e:
    print(f'[!] Error parsing data for report: {e}')
    exit

# POSTING
try:
    postToWebhook(DISCORD_WEBHOOK_URL,message)
except Exception as e:
    print(f'[!] Error issue posting to Discord: {e}')
    exit