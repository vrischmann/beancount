"""Fetch prices from the IEX 1.0 public API.

This is a really fantastic exchange API with a lot of relevant information.

Timezone information: There is currency no support for historical prices. The
output datetime is provided as a UNIX timestamp.
"""
__copyright__ = "Copyright (C) 2018  Martin Blais"
__license__ = "GNU GPLv2"

import datetime

from dateutil import tz
import requests
import os

from beancount.core.number import D
from beancount.prices import source


class IEXError(ValueError):
    "An error from the IEX API."


IEX_TOKEN = os.environ["IEX_TOKEN"]

def fetch_quote(ticker):
    """Fetch the latest price for the given ticker."""

    url = "https://cloud.iexapis.com/stable/stock/{}/quote?token={}".format(ticker.upper(), IEX_TOKEN)
    response = requests.get(url, timeout=300)
    if response.status_code != requests.codes.ok:
        raise IEXError("Invalid response ({}): {}".format(
            response.status_code, response.text))

    result = response.json()

    price = D(result['latestPrice']).quantize(D('0.01'))

    fr_timezone = tz.gettz("Europe/Paris")
    time = datetime.datetime.fromtimestamp(result['latestUpdate'] / 1000)
    time = time.astimezone(fr_timezone)

    return source.SourcePrice(price, time, 'EUR')


class Source(source.Source):
    "IEX API price extractor."

    def get_latest_price(self, ticker):
        """See contract in beancount.prices.source.Source."""
        return fetch_quote(ticker)

    def get_historical_price(self, ticker, time):
        """See contract in beancount.prices.source.Source."""
        raise NotImplementedError(
            "This is now implemented at https://iextrading.com/developers/docs/#hist and "
            "needs to be added here.")
