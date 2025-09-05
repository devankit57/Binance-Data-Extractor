from flask import Flask, jsonify, request
import requests
import pandas as pd
import datetime
import pytz

app = Flask(__name__)

# Health route (useful for Railway pings)
@app.route("/health")
def health():
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(tz)
    return jsonify({"status": "ok", "server_time": now.isoformat()})


# Binance Futures candle endpoint
@app.route("/candles")
def candles():
    symbol = request.args.get("symbol", "BTCUSDT")   # BTCUSDT / ETHUSDT
    interval = request.args.get("interval", "30m")  # e.g. 30m, 1h, 1d
    limit = request.args.get("limit", "50")

    try:
        url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        df = pd.DataFrame(data, columns=[
            "open_time","open","high","low","close","volume",
            "close_time","quote","trades","taker_base","taker_quote","ignore"
        ])

        # Convert open_time to Asia/Kolkata
        tz = pytz.timezone("Asia/Kolkata")
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(tz)

        result = df[["open_time", "open", "high", "low", "close", "volume"]].to_dict(orient="records")
        return jsonify({"symbol": symbol, "interval": interval, "candles": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Local dev: python app.py
    app.run(host="0.0.0.0", port=5000, debug=True)
