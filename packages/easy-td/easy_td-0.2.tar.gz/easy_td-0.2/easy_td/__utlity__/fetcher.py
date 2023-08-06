import requests as requests
import pandas   as pd
from aiohttp.client import request
import aiohttp
import asyncio


from .. import config
from .  import bell


def fetch(url, params, timeout=3, EXTRA=False):

    try:
        config.UPDATE_RATE_LIMIT()
        response = requests.get(url, params, timeout=timeout)

    except Exception as e:
        print(e)
        return {
            "error"     : str(e)
        }

    if "OPTIONS" in EXTRA:
        return pd.DataFrame({
            EXTRA["OPTIONS"] : response.json()
            })

    return pd.DataFrame(response.json())

def batch_fetcher(symbols, SYNC_FUNCTION, ASYNC_FUNCTION, ASYNC=False):
    if not ASYNC:
        return batch_sync(symbols, SYNC_FUNCTION)
    else: 
        return batch_async(symbols, SYNC_FUNCTION, ASYNC_FUNCTION)

def batch_sync(symbols, FETCH_FUNCTION):

    pass_bucket = []
    fail_bucket = []
        
    # print('building - passed')
    for ticker in symbols:
        data = FETCH_FUNCTION(ticker)
        pass_bucket.append(data) if "error" not in data else fail_bucket.append(ticker)
    
    # print('building - failed')
    for ticker in fail_bucket:
        # print(ticker)
        data = FETCH_FUNCTION(ticker)
        pass_bucket.append(data) if "error" not in data else fail_bucket.append(data)

    for ticker in fail_bucket:
        # print(ticker)
        data = FETCH_FUNCTION(ticker)
        pass_bucket.append(data) if "error" not in data else fail_bucket.append(data)
    
    if config.PD_OFF == True:
        return pass_bucket
    else:
        return pd.concat(pass_bucket,axis=0)

def batch_async(symbols, SYNC_FUNCTION, ASYNC_FUNCTION):
    loop = asyncio.get_event_loop()
    task = loop.create_task(async_helper(symbols, SYNC_FUNCTION, ASYNC_FUNCTION))
    data = loop.run_until_complete(task)
    return data

async def async_helper(symbols, SYNC_FUNCTION, ASYNC_FUNCTION):

    PD_TEMP_OFF = False
    if not config.PD_OFF:
        config.PD_OFF = True
        PD_TEMP_OFF   = True

    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    chunk_size = 100 # config.RATE_LIMIT  
    num_calls = int(len(symbols) / chunk_size) + 1

    subset_list = []
    all_data    = {}
    for i in (range(0, num_calls)):

        subset_symbols = symbols[chunk_size*i:chunk_size*(i+1)]
        print(subset_symbols)

        async with aiohttp.ClientSession() as session:
            ret = await asyncio.gather(*[ASYNC_FUNCTION(ticker, session) for ticker in subset_symbols][:chunk_size])
            subset_list += ret

        for row in subset_list:            
            try:
                ticker = list(row.keys())[0]
            except:
                continue
            
            if row[ticker] == 'error':
                try:
                    row[ticker] = SYNC_FUNCTION(ticker)
                except:
                    row[ticker] = { ticker: 'error' }
            
            all_data[ticker] = row[ticker]
        
        subset_list = []
        bell.cooldown()

    if not PD_TEMP_OFF:
        config.PD_OFF = False
        PD_TEMP_OFF      = False

    return pd.DataFrame.from_dict(all_data,orient='index')

