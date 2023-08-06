import sys
this = sys.modules[__name__]

import datetime as dt
import pytz     as pytz
tz=pytz.timezone('America/New_York')

this.API_KEY = None
this.PD_OFF  = False

this.TIMESTAMP  = dt.datetime.now(tz)
this.RATE_COUNT = 0
this.RATE_LIMIT = 120

from . import bell

def UPDATE_RATE_LIMIT():
    
    if (dt.datetime.now(tz) - this.TIMESTAMP).total_seconds() < 59:
        if this.RATE_COUNT >= this.RATE_LIMIT :
            bell.cooldown()

            this.RATE_COUNT = 0
            this.TIMESTAMP  = dt.datetime.now(tz)

    else:
            this.RATE_COUNT = 0
            this.TIMESTAMP  = dt.datetime.now(tz)

    # print(this.RATE_COUNT)
    # print(((dt.datetime.now(tz) - this.TIMESTAMP).total_seconds()))
    this.RATE_COUNT += 1


        
