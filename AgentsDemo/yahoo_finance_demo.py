import yfinance as yf
import json

def get_stock_price(ticker_symbol: str) -> str:
    """Fetch the current price of a stock given its ticker symbol"""

    try:
        stock = yf.Ticker(ticker_symbol.upper())
        print(stock.fast_info)
        price = stock.fast_info['last_price']
        currency = stock.fast_info["currency"]

        return json.dumps({
            "ticker": ticker_symbol.upper(),
            "price":price,
            "currency":currency
        })

    except Exception as e:
        print(f"Error fetching stock price for {ticker_symbol}: {e}")
        return json.dumps({
            "error":str(e)
        })


if __name__ == "__main__":
    print(get_stock_price("AAPL"))