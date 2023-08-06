from tradingview_scraper import *

a = ClassA.scraper(symbol = 'btc',
                wholePage = False,
                stratPage = 1,
                endPage = 2, 
                to_csv = False)

print(type(a))
print(a[0])