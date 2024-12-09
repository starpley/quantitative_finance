import os
import json
from datetime import datetime
from collections import defaultdict

class AveragePriceAggregator:
    def __init__(self, iex_token, polygon_key, alpha_key):
        self.yahoo_provider = YahooFinanceProvider()
        self.iex_provider = IEXCloudProvider(iex_token)
        self.polygon_provider = PolygonProvider(polygon_key)
        self.alpha_provider = AlphaVantageProvider(alpha_key)
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_data(self, stock_symbol):
        data = defaultdict(list)
        sources = [
            ("YahooFinance", self.yahoo_provider.get_quote),
            ("IEXCloud", self.iex_provider.get_quote),
            ("Polygon.io", self.polygon_provider.get_quote),
            ("AlphaVantage", self.alpha_provider.get_quote)
        ]
        
        for source_name, fetch_function in sources:
            try:
                price_data = fetch_function(stock_symbol)
                for price_entry in price_data:
                    date = price_entry["date"]
                    price = price_entry["price"]
                    data[date].append(price)
            except Exception as e:
                print(f"{source_name} error: {e}")
        
        return data

    def calculate_average_prices(self, stock_symbol):
        data = self.fetch_data(stock_symbol)
        average_prices = {}
        
        for date, prices in data.items():
            average_prices[date] = sum(prices) / len(prices)
        
        return average_prices

    def save_data(self, stock_symbol, data):
        cache_file = os.path.join(self.data_dir, f"{stock_symbol}_average.json")
        with open(cache_file, 'w') as f:
            json.dump(data, f)

    def load_data(self, stock_symbol):
        cache_file = os.path.join(self.data_dir, f"{stock_symbol}_average.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        else:
            data = self.calculate_average_prices(stock_symbol)
            self.save_data(stock_symbol, data)
            return data

# Example Usage
if __name__ == "__main__":
    iex_token = os.getenv('IEX_TOKEN')
    polygon_key = os.getenv('POLYGON_KEY')
    alpha_key = os.getenv('ALPHA_KEY')
    
    aggregator = AveragePriceAggregator(iex_token, polygon_key, alpha_key)
    stock_symbol = "AAPL"
    average_prices = aggregator.load_data(stock_symbol)
    print(f"Average prices for {stock_symbol}:")
    print(average_prices)