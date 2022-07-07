import yfinance as yf
import numpy as np
from scipy.stats import norm
import time
import math


def calculate_volatility(returns_arr):
    sum_of_returns = 0
    for i in range(len(returns_arr)):
        sum_of_returns += returns_arr[i]
    mean_return = sum_of_returns / len(returns_arr)
    sum_of_diff_squared = 0
    for i in range(len(returns_arr)):
        sum_of_diff_squared += (returns_arr[i] - mean_return) ** 2
    return math.sqrt(sum_of_diff_squared / len(returns_arr))


def call_pricing(S, K, r, T, sigma):
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def put_pricing(S, K, r, T, sigma):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma* np.sqrt(T)
    return K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)


time_period = input("Short-term or long-term derivatives pricing? (type short/long)")
if time_period != "short" and time_period != "long":
    print("Did not enter a valid input")
elif time_period == "short":
    time_to_maturity = float(input("Input a time to maturity for your derivative, in minutes"))
    strike_price = float(input("Input a strike price for your derivative"))
    current_3_month_bond_rate = 1.66
    current_inflation_rate = 8.2
    risk_free_rate = (1 + current_3_month_bond_rate) / (1 + current_inflation_rate) - 1

    BTC_Ticker = yf.Ticker("BTC-USD")
    # choose period of 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    df = BTC_Ticker.history(period="1d")

    counter = 1
    last_price = -1
    NUMBER_TRIALS = 10
    recent_prices = np.zeros(NUMBER_TRIALS)

    # measure historical price points by queueing yfinance every 3 minutes
    while counter < NUMBER_TRIALS:
        s = time.time()
        percentDone = 100.0 * (counter + 1) / NUMBER_TRIALS

        BTC_Ticker = yf.Ticker("BTC-USD")
        df = BTC_Ticker.history(period="max")
        last_price = df.Close[len(df.index) - 1]
        print("Live price is $", last_price)
        recent_prices[counter] = last_price
        counter += 1
        diff = time.time() - s
        time.sleep(150.0 - diff)
        print(percentDone, "% done fetching live prices")

    first_iteration = 1

    # continually update pricing and model
    while 1:
        s = time.time()
        spot_price = recent_prices[len(recent_prices) - 1]
        returns_arr = np.zeros(len(recent_prices) - 1)
        sum_of_returns = 0
        for i in range(len(returns_arr)):
            returns_arr[i] = recent_prices[i + 1] - recent_prices[i]
            sum_of_returns += returns_arr[i]
        mean_return = sum_of_returns / len(returns_arr)
        sum_of_diff_squared = 0
        for i in range(len(returns_arr)):
            sum_of_diff_squared += (returns_arr[i] - mean_return) ** 2
        volatility = math.sqrt(sum_of_diff_squared / len(returns_arr))
        call_price = call_pricing(spot_price, strike_price, risk_free_rate, time_to_maturity, volatility)
        put_price = put_pricing(spot_price, strike_price, risk_free_rate, time_to_maturity, volatility)
        print("Call price is $", call_price, "and put price is $", put_price)
        diff = time.time() - s
        time.sleep(150.0 - diff)

        BTC_Ticker = yf.Ticker("BTC-USD")
        df = BTC_Ticker.history(period="max")
        last_price = df.Close[len(df.index) - 1]
        print("Live price is $", last_price)
        for i in range(len(recent_prices)-1):
            recent_prices[i] = recent_prices[i+1]
        recent_prices[len(recent_prices)-1] = last_price
else:
    time_to_maturity = float(input("Input a time to maturity for your derivative, in days"))
    strike_price = float(input("Input a strike price for your derivative"))
    current_3_month_bond_rate = 1.66
    current_inflation_rate = 8.2
    risk_free_rate = (1 + current_3_month_bond_rate) / (1 + current_inflation_rate) - 1

    BTC_Ticker = yf.Ticker("BTC-USD")
    # choose period of 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    df = BTC_Ticker.history(period="1y")
    NUMBER_TRIALS = 10
    returns_arr = np.zeros(NUMBER_TRIALS)
    for i in range(NUMBER_TRIALS):
        returns_arr[i] = df.Close[len(df.index) - 1 - i] - df.Open[len(df.index) - 1 - i]
    volatility = calculate_volatility(returns_arr)
    spot_price = df.Close[len(df.index)-1]
    call_price = call_pricing(spot_price, strike_price, risk_free_rate, time_to_maturity, volatility)
    put_price = put_pricing(spot_price, strike_price, risk_free_rate, time_to_maturity, volatility)
    print("Call price is $", call_price, "and put price is $", put_price)
