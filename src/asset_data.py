import polars as pl
import yfinance as yf
import os
import json

class AssetData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        # Load data from the CSV file
        return pl.read_csv(self.file_path)

    def get_stock_history(self, ticker_symbol, start_date, end_date):
        # Define the cache file path for stock history
        history_cache_file = f'{ticker_symbol}_history_cache.json'
        
        # Check if the cache file exists
        if os.path.exists(history_cache_file):
            # Load data from the cache file
            with open(history_cache_file, 'r') as f:
                cached_history = json.load(f)
            return pl.DataFrame(cached_history)
        else:
            # Fetch stock history from yfinance
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(start=start_date, end=end_date)
            hist_df = pl.DataFrame(hist)
            # Cache the stock history data to a JSON file
            with open(history_cache_file, 'w') as f:
                json.dump(hist_df.to_dict(), f)
            return hist_df

    def get_holdings(self):
        holdings = set()
        for row in self.data.iter_rows(named=True):
            holdings.add((row['Ticker symbol'], row['Quantity']))
        return holdings