
#%%
import pandas as pd
import websocket,json

#%%
def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("closed")
#%%
coin='btc'
interval='1m'
socket= f"wss://stream.binance.com:9443/ws/{coin}usdt@kline_{interval}"
ws = websocket.WebSocketApp(socket, on_message=on_message, on_close=on_close)
#%%
ws.run_forever()
ws.close()
# %%

# %%
