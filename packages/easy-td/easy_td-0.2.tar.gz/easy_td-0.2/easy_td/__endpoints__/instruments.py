import requests
from aiohttp.client import request
import aiohttp
import asyncio


from ..__utlity__ import config 
from ..__utlity__ import fetcher

def get(ticker):
    endpoint = f'https://api.tdameritrade.com/v1/instruments?&symbol={ticker}&projection={"fundamental"}'
    payload = {'apikey': config.API_KEY}

    response = fetcher.fetch(
                    url=endpoint,
                    params=payload
                )

    return response

async def get_async(ticker, session):
    try:
        endpoint = f'https://api.tdameritrade.com/v1/instruments?&symbol={ticker}&projection={"fundamental"}'
        payload = {'apikey': config.API_KEY}
        timeout = aiohttp.ClientTimeout(total=2)
        async with session.get(endpoint,params=payload, timeout=timeout) as response:
            resp = await response.json()

            # {'error': "Individual App's transactions per seconds restriction reached. Please contact us with further questions"}
            if 'error' in resp.keys():
                return {ticker : resp}

            # fundamental : dict = resp[ticker][ticker]['fundamental']
            # fundamental['cusip']       = resp[ticker][ticker]['cusip']
            # fundamental['symbol']      = resp[ticker][ticker]['symbol']
            # fundamental['description'] = resp[ticker][ticker]['description']
            # fundamental['exchange']    = resp[ticker][ticker]['exchange']
            # fundamental['assetType']   = resp[ticker][ticker]['assetType']

            return resp

    except Exception as e:
        return {ticker : {'error' : str(e)}}

def snapshot(symbols, ASYNC=False):
    SYNC_FUNCTION  = get
    ASYNC_FUNCTION = get_async
    return fetcher.batch_fetcher(symbols, get, get_async, ASYNC)


