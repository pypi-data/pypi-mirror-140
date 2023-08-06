import requests
import pandas as pd

from ..__utlity__ import config 
from ..__utlity__ import fetcher

def get(ticker):
    endpoint = 'https://api.tdameritrade.com/v1/marketdata/chains'
    payload = {'apikey': config.API_KEY, 'symbol':ticker, 'strikeCount':100 , 'strategy': 'SINGLE'}

    response = fetcher.fetch(
                    url=endpoint,
                    params=payload,
                    EXTRA={
                        "OPTIONS" : ticker
                    }
                )

    return response

def snapshot(symbols=[]):
    if not symbols: 
        symbols = list(pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', header = 0)[0]['Symbol'])

    DF_CONCAT_LIST = []
    for ticker in symbols:
        DF_CONCAT_LIST.append(pd.DataFrame(get(ticker)))

    return pd.concat(DF_CONCAT_LIST, axis=1).T

async def get_async(ticker, session):
    try:
        endpoint = 'https://api.tdameritrade.com/v1/marketdata/chains'
        payload = {'apikey': config.API_KEY, 'symbol':ticker, 'strikeCount':100 , 'strategy': 'SINGLE'}

        timeout = aiohttp.ClientTimeout(total=2)
        async with session.get(endpoint,params=payload, timeout=timeout) as response:
            resp = await response.json()

            # {'error': "Individual App's transactions per seconds restriction reached. Please contact us with further questions"}
            if 'error' in resp.keys():
                print(resp)
                return {ticker : None}

            return {ticker: resp}

    except Exception as e:
        print(e)
        return {ticker : None}

