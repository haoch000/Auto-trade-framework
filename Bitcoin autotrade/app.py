# set FLASK_ENV=development
# flask run

from flask import Flask, render_template, request, flash,redirect, jsonify
from werkzeug.utils import redirect
import config,csv
from binance.client import Client
from binance.enums import *

app = Flask(__name__)
app.secret_key = ' '
client = Client (config.API_KEY,config.API_SECRET)

@app.route("/")
def index():
    title = 'CoinView'

    account= client.get_account()

    balances= account['balances']

    exchange_info = client.get_exchange_info()

    symbols = exchange_info['symbols']

    return render_template('index.html',title=title, my_balancs=balances,symbols=symbols)

@app.route("/buy",methods=["POST"])
def buy():
    print(request.form)
    try:
        order = client.create_margin_order(symbol=request.form['symbol'],
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            #timeInForce=TIME_IN_FORCE_GTC,
            quantity=request.form['quantity'])
    except Exception as e:
        flash(e.message, "error")
    return redirect('/')

@app.route("/sell")
def sell():
    return "sell"

@app.route("/settings")
def settings():
    return "settings"

@app.route("/history")
def history():
    candlesticks=client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 Sep, 2021", "28 Sep, 2021")

    processed_candlesticks = []

    for data in candlesticks:
        candlestick = {
            "time": data[0]/1000,
            "open": data[1],
            "high": data[2],
            "low": data[3],
            "close": data[4]
            #"volumn":data[5]
             }

        processed_candlesticks.append(candlestick)

    return jsonify(processed_candlesticks)
