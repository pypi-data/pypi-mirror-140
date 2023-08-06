from tradingview_scraper import *

a = ClassA.scraper(symbol = 'btc',
                wholePage = False,
                startPage = 1,
                endPage = 2, 
                to_csv = False,
                return_json=True)

# print(a)
print(a.keys())