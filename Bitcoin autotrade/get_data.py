#%%
import config
from binance.client import Client
import csv
import talib
#%%

client = Client (config.API_KEY,config.API_SECRET)

prices = client.get_all_tickers()

candles = client.get_klines(symbol='ETHUSDT', interval=Client.KLINE_INTERVAL_1MINUTE)

print(len(candles))
# %%
csvfile = open('15min.csv','w',newline='\n')
candlestick_writer = csv.writer(csvfile, delimiter=',')

klines = client.get_historical_klines("ETHUSDT", 
Client.KLINE_INTERVAL_15MINUTE, "1 Apr, 2020", "31 Oct, 2021")

for stick in klines:
    candlestick_writer.writerow(stick)

csvfile.close()
# %%


