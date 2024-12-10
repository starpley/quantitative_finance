import polars as pl
import yfinance as yf
import os
import json
from loguru import logger

'''
Sample csv file:

Stock name,Ticker symbol,Shares owned,Purchase price,Current price,Total value
Apple Inc.,AAPL,100,150.00,170.00,17000.00
Alphabet Inc.,GOOG,50,2000.00,2100.00,105000.00
Microsoft Corp.,MSFT,200,250.00,270.00,54000.00
Tesla Inc.,TSLA,75,700.00,750.00,56250.00

'''
class AssetData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()
        self.stock_history_cache = {}

    def load_data(self):
        logger.info(f"Loading data from CSV file: {self.file_path}")
        df = pl.read_csv(self.file_path)
        fixed_columns = {
            "Stock name": "stock_name",
            "Ticker symbol": "ticker",
            "Shares owned": "shares_owned",
            "Purchase price": "purchase_price",
            "Current price": "current_price",
            "Total value": "total_value"
        }
        df = df.rename(fixed_columns)
        logger.debug(f"Data loaded with columns: {df.columns}")
        return df

    def get_stock_history(self, ticker_symbol, start_date, end_date):
        logger.info(f"Fetching stock history for {ticker_symbol} from {start_date} to {end_date}")
        
        # Check if the data is already in memory
        if ticker_symbol in self.stock_history_cache:
            logger.debug(f"Stock history for {ticker_symbol} found in memory")
            return self.stock_history_cache[ticker_symbol]
        
        # Define the cache file path for stock history
        history_cache_file = f'{ticker_symbol}_history_cache.json'
        
        # Check if the cache file exists
        if os.path.exists(history_cache_file):
            logger.debug(f"Cache file found for {ticker_symbol}: {history_cache_file}")
            with open(history_cache_file, 'r') as f:
                cached_history = json.load(f)
                self.stock_history_cache[ticker_symbol] = pl.from_dicts(cached_history)
            return self.stock_history_cache[ticker_symbol]
        
        # Fetch stock history from yfinance
        logger.debug(f"No cache file found for {ticker_symbol}, fetching from yfinance")
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(start=start_date, end=end_date)
        hist_df = pl.DataFrame(hist.to_dict())
        
        # Cache the stock history data to memory and a JSON file
        self.stock_history_cache[ticker_symbol] = hist_df
        with open(history_cache_file, 'w') as f:
            json.dump(hist_df.to_dict(), f)
        logger.debug(f"Stock history for {ticker_symbol} cached to {history_cache_file}")
        
        return hist_df

    def get_holdings(self):
        logger.info("Getting holdings from data")
        holdings = set()
        for row in self.data.iter_rows(named=True):
            holdings.add((row['ticker'], row['shares_owned']))
        logger.debug(f"Holdings retrieved: {holdings}")
        return holdings

    def fetch_all_stock_histories(self, start_date, end_date):
        logger.info("Fetching stock history for all holdings")
        stock_histories = {}
        for ticker, _ in self.get_holdings():
            stock_histories[ticker] = self.get_stock_history(ticker, start_date, end_date)
        logger.debug("Stock histories fetched for all holdings")
        return stock_histories