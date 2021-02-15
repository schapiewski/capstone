from alpha_vantage.timeseries import TimeSeries
import requests
from models import Ticker
import time
import datetime

api_key = 'I2CGXL68P1CJ9XNP'
tag_list = ['PLTR', 'TSLA', 'GOOG', 'NOK', 'GME', 'AMC', 'DAL', 'CCL']
print(len(tag_list))
for k in range(1, len(tag_list)):
    ts = TimeSeries(key=api_key, output_format='pandas')
    data_ts, meta_data_ts = ts.get_daily(symbol=tag_list[k])

    ti = TimeSeries(key=api_key, output_format='pandas')
    data_ti, meta_data_ti = ti.get_daily(symbol=tag_list[k])

    ts_df = data_ts
    ti_df = data_ti

    payload = {'function': 'OVERVIEW', 'symbol': tag_list[k], 'apikey': 'YX9741BHQFXIYA0B'}
    r = requests.get('https://www.alphavantage.co/query', params=payload)
    r = r.json()
    print(r)
    stockName = r['Name']
    sector = r['Sector']
    marketcap = r['MarketCapitalization']
    peratio = r['PERatio']
    yearhigh = r['52WeekHigh']
    yearlow = r['52WeekLow']
    eps = r['EPS']

    timeseries = ts_df.to_dict(orient='records')
    closingprice = []
    for k in timeseries:
        closingprice.append(k['4. close'])
    lowprice = []
    for k in timeseries:
        closingprice.append(k['3. low'])
    highprice = []
    for k in timeseries:
        closingprice.append(k['2. high'])
    openprice = []
    for k in timeseries:
        closingprice.append(k['1. open'])
    pricedata = {
        'close': [closingprice],
        'open': [openprice],
        'high': [highprice],
        'low': [lowprice],
    }
    # miscellaneous stuff
    day = datetime.datetime.now()
    day = day.strftime("%A")


    def human_format(num):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        # add more suffixes if you need them
        return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


    marketcap = int(marketcap)
    marketcap = human_format(marketcap)
    closingprice = closingprice[0:15]
    currentPrice = closingprice[0]
    previousClosingPrice = closingprice[1]
    priceChange = closingprice[0] - closingprice[1]
    decimalChange = closingprice[0] / closingprice[1]
    PosNegChange = decimalChange - 1
    percentageChange = PosNegChange * 100
    print(k, tag_list[k])
    test = Ticker(ticker=tag_list[k], stock_name=stockName, sector=sector, market_cap=marketcap, current_price=currentPrice, previous_closing_price=previousClosingPrice, percentage_change=percentageChange, year_high=yearhigh, year_low=yearlow, price_change=priceChange)
    test.save()
    print("Saving ", stockName, " to Database")
    print("Database Object", test)
    if k%4 == 0:
        time.sleep(70)