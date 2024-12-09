import unittest
from src.portfolio import Portfolio
from src.backtester import Backtester

class TestBacktester(unittest.TestCase):
    def setUp(self):
        self.portfolio = Portfolio()
        self.portfolio.add_stock('AAPL', 100)
        self.portfolio.add_stock('GOOG', 50)
        self.portfolio.add_stock('MSFT', 200)
        self.portfolio.add_stock('TSLA', 75)
        self.backtester = Backtester(self.portfolio)

    def test_backtest_portfolio(self):
        historical_data_df = self.backtester.backtest_portfolio()
        self.assertFalse(historical_data_df.is_empty())
        self.assertEqual(len(historical_data_df.columns), 4)

    def test_calculate_performance(self):
        self.backtester.backtest_portfolio()
        performance = self.backtester.calculate_performance()
        self.assertTrue(isinstance(performance, float))
        self.assertGreaterEqual(performance, -1.0)  # Performance should be within a valid range

if __name__ == '__main__':
    unittest.main()