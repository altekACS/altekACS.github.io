import yfinance as yf
import json

def get_stock_price(ticker = None):
    
    res = {}

    # ticker = request.args.get('ticker')
    if not ticker:
        res['status_code'] = 400
        res['json'] = {"error": "Missing ticker parameter"}
        return res

    stock = yf.Ticker(ticker)
    stock_info = stock.history(period="1d")

    if stock_info.empty:
        res['status_code'] = 404
        res['json'] = {"error": "Invalid ticker or no data available"}
        return res

    latest_price = stock_info["Close"].iloc[-1]
    res['status_code'] = 200
    res['json'] = {"ticker": ticker, "price": latest_price}
    return res

# if __name__ == '__main__':
#     response = get_stock_price('2330.TW')
#     stock_data = response['json']
#     company_price = stock_data["price"]
#     print(company_price)
        
