import ccxt
import config
import pandas as pd
import numpy as np
import schedule
import warnings
from datetime import datetime
import time
warnings.filterwarnings('ignore')
pd.set_option('display.max_rows',None)

exchange = ccxt.binance({
    'apiKey': config.API_KEY,
    'secret': config.API_SECRET
})
# markets = exchange.load_markets()
# ticker = exchange.fetch_ticker('BTC/USDT')
# order_book = exchange.fetch_order_book('ETH/USDT')
# balances = exchange.fetch_balance()
# exchange.create_market_buy_order


# basic upper band = (high-low)/2 + multiplier * atr
# basic lower band = (high-low)/2 - multiplier * atr
def tr(df):
    df['pre_close']=df['close'].shift(1)
    df['high-low']=df['high']-df['low']
    df['high-pre_c']=abs(df['high'] - df['pre_close'])
    df['low-pre_c']=abs(df['low'] - df['pre_close'])
    tr = df[['high-low','high-pre_c','low-pre_c']].max(axis=1)
    return tr

def get_atr(df,period):
    df['tr'] = tr(df)
    atr= df['tr'].rolling(period).mean()
    return atr

def supertrend(df,period=7, multiplier=3):
    df['atr'] = get_atr(df,period=period)
    df['upperband'] = ((df['high'] + df['low'])/2) + (multiplier * df['atr'])
    df['lowerband'] = ((df['high'] + df['low'])/2) - (multiplier * df['atr'])
    df['in_uptrend'] = True
    for current in range(1,len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]

    return df
in_position = False
def check_signal(df):
    global in_position

    print(df.tail(5))
    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1

    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
        print('signal to buy')
        if not in_position:
            order = exchange.create_market_buy_order('ETH/USDT',0.05)
            print(order)
            in_position = True
        else:
            print('already in position, nothing to conduct')

    if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
        print('signal to sell')
        if not in_position:
            order = exchange.create_market_buy_order('ETH/USDT',0.05)
            print(order)


def job():
    print(f"fetching new bar for {datetime.now().isoformat()}")
    bars = exchange.fetch_ohlcv('ETH/USDT',timeframe='15m',limit=5)
    df = pd.DataFrame(bars[:-1],columns=['time','open','high','low','close','volume'])
    df['time'] = pd.to_datetime(df['time'],unit='ms')
    print(df)
    supertrend_data = supertrend(df)
    check_signal(supertrend_data)

schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(0.1)
