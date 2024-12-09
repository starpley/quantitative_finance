import unittest
import polars as pl
from src.stock_data_loader import StockDataLoader

class TestStockDataLoader(unittest.TestCase):
    def setUp(self):
        self.loader = StockDataLoader('data/portfolio_positions.csv')

    def test_load_data(self):
        df = self.loader.load_data()
        self.assertIsInstance(df, pl.DataFrame)
        self.assertEqual(df.columns, ['Stock name', 'Ticker symbol', 'Shares owned', 'Purchase price', 'Current price', 'Total value'])

    def test_get_stock_history(self):
        ticker_symbol = 'AAPL'
        start_date = '2023-01-01'
        end_date = '2023-12-31'
        hist = self.loader.get_stock_history(ticker_symbol, start_date, end_date)
        self.assertIsInstance(hist, pl.DataFrame)
        self.assertTrue('Close' in hist.columns)

    def test_update_current_prices(self):
        updated_portfolio = self.loader.update_current_prices()
        self.assertIsInstance(updated_portfolio, pl.DataFrame)
        self.assertTrue('Current price' in updated_portfolio.columns)

if __name__ == '__main__':
    unittest.main()