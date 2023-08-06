import requests

from ..__utlity__ import config 
from ..__utlity__ import fetcher

import pandas as pd

def snapshot():
    endpoint = 'https://api.tdameritrade.com/v1/instruments'
    payload ={
        'apikey': config.API_KEY, #your api key goes here
        'symbol': '[A-Z].*',
        'projection' : 'symbol-regex'
    }
    try:
        response = requests.get(
                        url=endpoint,
                        params=payload
                    )
    except:
        response = pd.DataFrame()

    return pd.DataFrame(response.json()).T

def list():
    return snapshot().index.values