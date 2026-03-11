import yfinance as yf

def main():
    
    print("Starte TSLA Abruf …")
    # Tesla-Ticker
    ticker = yf.Ticker("TSLA")

    # Hole die letzten 5 Tage im 1h-Intervall
    df = ticker.history(period="5d", interval="1h")
    
    print("Zeilen:", len(df))   
    print("--- Historische Daten von Tesla (TSLA) ---")
    print(df.tail())

if __name__ == "__main__":
    main()