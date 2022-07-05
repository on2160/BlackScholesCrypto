import yfinance as yf

BTC_Ticker = yf.Ticker("BTC-USD")
#choose period of 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
BTC_Data = BTC_Ticker.history(period="max")
print(BTC_Data)
