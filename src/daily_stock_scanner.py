import yfinance as yf
import pandas as pd

# Hardcoded list of 15 tech/growth stocks (AAPL, NVDA, TSLA, etc.) to scan
# Download recent price data, computes a few technical metrics, scores each stock, and reports the ones that look strongest.
TICKERS = [

    "AAPL","NVDA","TSLA","MSFT","AMZN",

    "META","AMD","PLTR","SOFI","COIN",

    "RIVN","SNAP","SHOP","ROKU","NIO"

]

# This helper computes the 14-day RSI from a price series.
def calculate_rsi(data, period=14):

    # Computes day-to-day price changes.
    delta = data.diff()

    # The average positive change over the window.
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()

    # The average negative change over the window.
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss

    # Returns the RSI value, which ranges from 0 to 100. Higher values indicate stronger momentum.
    # Standard relative strength index for the closing prices.
    rsi = 100 - (100 / (1 + rs))

    return rsi

# Downloads 6 months of daily price data for the given ticker, computes the 50-day SMA, 20-day volume MA, 
# and RSI, and scores the stock based on momentum, volume spike, and RSI strength. Returns a dictionary with 
# the analysis results.
def analyze_stock(ticker):

    try:

        df = yf.download(ticker, period="6mo", interval="1d", progress=False)

        if len(df) < 50:

            return None

        # Compute the 50-day Simple Moving Average (SMA) of the closing price.
        df["SMA50"] = df["Close"].rolling(50).mean()

        # Compute the 20-day Moving Average of the trading volume.
        df["Volume_MA"] = df["Volume"].rolling(20).mean()

        # Compute the 14-day Relative Strength Index (RSI) of the closing price.
        df["RSI"] = calculate_rsi(df["Close"])

        # Analyze the most recent data point to determine if the stock has strong momentum, 
        # a volume spike, and a strong RSI.
        last = df.iloc[-1]

        # Momentum: Price above the 50-day SMA suggests an uptrend.
        momentum = last["Close"] > last["SMA50"]

        # Volume Spike: Current volume significantly above the 20-day average suggests increased interest.
        volume_spike = last["Volume"] > last["Volume_MA"] * 1.5

        # RSI Strength: An RSI above 60 indicates strong momentum without being overbought.    
        strong_rsi = last["RSI"] > 60

        # Each condition contributes 1 point to the score, for a maximum of 3. Higher scores indicate stronger setups.
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

# This drives the scan over all tickers.
# It collects the analysis results, filters for stocks with a score of 2 or higher, and outputs the top candidates 
# in a sorted table.
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

 