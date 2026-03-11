import yfinance as yf
import pandas as pd

# Aktienliste (kann später erweitert werden)

TICKERS = [

    "AAPL","NVDA","TSLA","MSFT","AMZN",

    "META","AMD","PLTR","SOFI","COIN",

    "RIVN","SNAP","SHOP","ROKU","NIO"

]

def calculate_rsi(data, period=14):

    delta = data.diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()

    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def analyze_stock(ticker):

    try:

        df = yf.download(ticker, period="6mo", interval="1d", progress=False)

        if len(df) < 50:

            return None

        df["SMA50"] = df["Close"].rolling(50).mean()

        df["Volume_MA"] = df["Volume"].rolling(20).mean()

        df["RSI"] = calculate_rsi(df["Close"])

        last = df.iloc[-1]

        momentum = last["Close"] > last["SMA50"]

        volume_spike = last["Volume"] > last["Volume_MA"] * 1.5

        strong_rsi = last["RSI"] > 60

        score = sum([momentum, volume_spike, strong_rsi])

        return {

            "ticker": ticker,

            "price": round(last["Close"],2),

            "rsi": round(last["RSI"],2),

            "volume": int(last["Volume"]),

            "score": score

        }

    except:

        return None


def run_scanner():

    results = []

    for ticker in TICKERS:

        data = analyze_stock(ticker)

        if data and data["score"] >= 2:

            results.append(data)

    df = pd.DataFrame(results)

    if len(df) > 0:

        df = df.sort_values("score", ascending=False)

        print("\nTop Trading Kandidaten:\n")

        print(df)

        df.to_csv("scanner_results.csv", index=False)

    else:

        print("Keine starken Setups gefunden")


if __name__ == "__main__":

    run_scanner()
 