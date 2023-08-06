# easy-finweb
A python client to fetch public financial data from the web.  Included categories below.
- sp500 (sector and ticker info)
- earnings 
- highest option iv
- market suspensions

# Example Usage
> Note: strucure uses declarative functional format 
> 
> - [package] -> [target_data] -> [get/snapshot]
  
> Note: get() function is for single tickers and snapshot() is for all tickers (in universe)
```
import easy_finweb as web

var = web.sp500_sectors.get("AAPL")
print(var)

var = web.sp500_sectors.snapshot()
print(var)

var = web.sp500_sectors.get("AAPL")
print(var)

var  = web.earnings.get("AAPL")
print(var)

var  = web.earnings.snapshot()
print(var)

var = web.highest_iv.get()
print(var)

# input: historical (bool)   # get historical suspensions rather than current
var = web.suspensions.get(historical=False)
print(var)
```
