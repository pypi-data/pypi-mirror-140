# easy_td
A python client for the td api.  Uses a declarative functional format with rate limit protection

> Note: endpoint names are conventional from td's rest api

>  [td] -> [endpoint] -> [get/snapshot]

# Example Usage 
```
# setting config variables 
# Pandas True by default
td.config.API_KEY = "MY_EXAMPLE_API_KEY"
td.config.PD_OFF      = False 
td.config.RATE_LIMIT  = 120 

# fetching symbols
symbols : list = td.symbols.get()

# fetching instruments (equity information)
AAPL_INFO  : pd = td.instruments.get('AAPL')
INFO_SNAP  : pd = td.instruments.snapshot()

# fetching option chains 
AAPL_CHAIN   : pd = td.option_chains.get("AAPL")
OPTIONS_SNAP : pd = td.option_chains.snapshot()

```
