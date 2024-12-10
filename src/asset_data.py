import polars as pl
import yfinance as yf
import os
import json
from loguru import logger
import pyarrow

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

    def check_cache_memory(self, ticker_symbol):
        if ticker_symbol in self.stock_history_cache:
            logger.debug(f"Stock history for {ticker_symbol} found in memory")
            return self.stock_history_cache[ticker_symbol]
        return None

    def check_cache_file(self, ticker_symbol):
        history_cache_file = f'cache/{ticker_symbol}_history_cache.json'
        if os.path.exists(history_cache_file):
            logger.debug(f"Cache file found for {ticker_symbol}: {history_cache_file}")
            with open(history_cache_file, 'r') as f:
                cached_history = json.load(f)
                self.stock_history_cache[ticker_symbol] = pl.from_dicts(cached_history)
            return self.stock_history_cache[ticker_symbol]
        return None

    def fetch_from_yfinance(self, ticker_symbol, start_date, end_date):
        try:
            logger.debug(f"No cache file found for {ticker_symbol}, fetching from yfinance")
            stock = yf.Ticker(ticker_symbol)
            hist = stock.history(start=start_date, end=end_date)
            
            # Ensure timestamps are converted correctly
            hist.index = hist.index.strftime('%Y-%m-%d')
            hist_df = pl.DataFrame(hist.to_dict())
            return hist_df
        except Exception as e:
            logger.error(f"Failed to fetch stock history for {ticker_symbol}: {e}")
            return None
        
    def cache_stock_history(self, ticker_symbol, hist_df):
        self.stock_history_cache[ticker_symbol] = hist_df
        history_cache_file = f'{ticker_symbol}_history_cache.json'
        try:
            # Convert DataFrame to dict before dumping to JSON
            hist_dict = hist_df.to_pandas().to_dict(orient='list')
            with open(history_cache_file, 'w') as f:
                json.dump(hist_dict, f)
            logger.debug(f"Stock history for {ticker_symbol} cached to {history_cache_file}")
        except Exception as e:
            logger.error(f"Failed to cache stock history for {ticker_symbol}: {e}")

    def get_stock_history(self, ticker_symbol, start_date, end_date):
        logger.info(f"Fetching stock history for {ticker_symbol} from {start_date} to {end_date}")
        
        # Check if the data is already in memory
        history = self.check_cache_memory(ticker_symbol)
        if history is not None:
            return history
        
        # Check if the cache file exists
        history = self.check_cache_file(ticker_symbol)
        if history is not None:
            return history
        
        # Fetch stock history from yfinance
        history = self.fetch_from_yfinance(ticker_symbol, start_date, end_date)
        if history is not None:
            self.cache_stock_history(ticker_symbol, history)
        
        return history

    def get_holdings(self):
        logger.info("Getting holdings from data")
        holdings = []
        for row in self.data.iter_rows(named=True):
            holdings.append((row['stock_name'], row['ticker'], row['shares_owned']))
        logger.debug(f"Holdings retrieved: {holdings}")
        return holdings

    def fetch_all_stock_histories(self, start_date, end_date):
        logger.info("Fetching stock history for all holdings")
        stock_histories = {}
        for _, ticker, _ in self.get_holdings():
            stock_histories[ticker] = self.get_stock_history(ticker, start_date, end_date)
        logger.debug("Stock histories fetched for all holdings")
        return stock_histories