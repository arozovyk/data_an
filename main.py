# This example uses Python 2.7 and the python-request library.

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical'
parameters = {
    'time_start': '1651536000',
    'time_end': '1680480000',
    'convert': 'EUR'
}
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '4a4da71a-6164-4f07-b17c-f68fc4c8039b',
}

session = Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    entries = json.loads(response.text)
    """ mapped_entries = [{"symbol": entry["symbol"],
                       "quote": entry["quote"]} for entry in entries["data"]] """

    print(json.dumps(entries, indent=4))

except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)
