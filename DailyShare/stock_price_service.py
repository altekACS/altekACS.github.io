import yfinance as yf
import json

def get_stock_price(ticker = None):
    
    res = {}

    # ticker = request.args.get('ticker')
    if not ticker:
        res['status_code'] = 400
        res['json'] = json.dumps({"error": "Missing ticker parameter"})
        return res

    stock = yf.Ticker(ticker)
    stock_info = stock.history(period="1d")

    if stock_info.empty:
        res['status_code'] = 404
        res['json'] = json.dumps({"error": "Invalid ticker or no data available"})
        return res

    latest_price = stock_info["Close"].iloc[-1]
    res['status_code'] = 200
    res['json'] = json.dumps({"ticker": ticker, "price": latest_price})
    return res

# if __name__ == '__main__':
#     response = get_stock_price('2330.TW')
#     print(response.json)
        
