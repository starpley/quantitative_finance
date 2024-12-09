import os
import json
from yfinance import Ticker as YahooFinanceProvider
from iexfinance.stocks import Stock as IEXCloudProvider
from polygon import BaseClient as PolygonProvider
from alpha_vantage.timeseries import TimeSeries as AlphaVantageProvider

class Portfolio:
    def __init__(self, iex_token, polygon_key, alpha_key):
        self.stocks = {}
        self.yahoo_provider = YahooFinanceProvider
        self.iex_provider = IEXCloudProvider(iex_token)
        self.polygon_provider = PolygonProvider(polygon_key)
        self.alpha_provider = AlphaVantageProvider(key=alpha_key)
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def add_stock(self, stock_symbol, shares):
        self.stocks[stock_symbol] = shares

    def remove_stock(self, stock_symbol):
        if stock_symbol in self.stocks:
            del self.stocks[stock_symbol]

    def fetch_data(self, stock_symbol):
        data = []
        sources = [
            ("YahooFinance", lambda symbol: self.yahoo_provider(symbol).info['regularMarketPrice']),
            ("IEXCloud", lambda symbol: self.iex_provider(symbol).get_price()),
            ("Polygon.io", lambda symbol: self.polygon_provider.reference_ticker_details(symbol).ticker),
            ("AlphaVantage", lambda symbol: self.alpha_provider.get_intraday(symbol=symbol, interval='1min')[0])
        ]
        
        for source_name, fetch_function in sources:
            try:
                price = fetch_function(stock_symbol)
                data.append({
                    "symbol": stock_symbol,
                    "price": price,
                    "timestamp": "2024-12-08T00:00:00Z",  # Replace with actual timestamp
                    "source": source_name
                })
            except Exception as e:
                print(f"{source_name} error: {e}")
        
        return data

    def save_data(self, stock_symbol, data):
        cache_file = os.path.join(self.data_dir, f"{stock_symbol}.json")
        with open(cache_file, 'w') as f:
            json.dump(data, f)

    def load_data(self, stock_symbol):
        cache_file = os.path.join(self.data_dir, f"{stock_symbol}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        else:
            data = self.fetch_data(stock_symbol)
            self.save_data(stock_symbol, data)
            return data

    def get_stock_price(self, stock_symbol):
        # Load and aggregate data
        data = self.load_data(stock_symbol)
        if data:
            # Assuming we take the average price from multiple sources as the final price
            prices = [entry['price'] for entry in data]
            return sum(prices) / len(prices)
        else:
            raise Exception("Failed to get the stock price from all sources")

    def get_portfolio_value(self):
        total_value = 0
        for stock_symbol, shares in self.stocks.items():
            current_price = self.get_stock_price(stock_symbol)
            total_value += shares * current_price
        return total_value