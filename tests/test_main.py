import unittest
import json
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from main import load_api_tokens, initialize_portfolio, initialize_aggregator, add_stocks_to_portfolio, prepare_stock_data_for_optimization, optimize_portfolio, calculate_actual_portfolio_risk_return, generate_and_backtest_portfolios
from src.portfolio import Portfolio
from src.average_price_aggregator import AveragePriceAggregator
from src.optimizer import PortfolioOptimizer

class MainFunctionTests(unittest.TestCase):

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"IEX_TOKEN": "iex_token", "POLYGON_KEY": "polygon_key", "ALPHA_KEY": "alpha_key"}')
    def test_load_api_tokens(self, mock_open):
        tokens = load_api_tokens()
        self.assertEqual(tokens['IEX_TOKEN'], 'iex_token')
        self.assertEqual(tokens['POLYGON_KEY'], 'polygon_key')
        self.assertEqual(tokens['ALPHA_KEY'], 'alpha_key')

    @patch('src.portfolio.Portfolio')
    def test_initialize_portfolio(self, MockPortfolio):
        tokens = {'IEX_TOKEN': 'iex_token', 'POLYGON_KEY': 'polygon_key', 'ALPHA_KEY': 'alpha_key'}
        portfolio = initialize_portfolio(tokens)
        MockPortfolio.assert_called_once_with('iex_token', 'polygon_key', 'alpha_key')
        self.assertIsInstance(portfolio, Portfolio)

    @patch('src.average_price_aggregator.AveragePriceAggregator')
    def test_initialize_aggregator(self, MockAggregator):
        tokens = {'IEX_TOKEN': 'iex_token', 'POLYGON_KEY': 'polygon_key', 'ALPHA_KEY': 'alpha_key'}
        aggregator = initialize_aggregator(tokens)
        MockAggregator.assert_called_once_with('iex_token', 'polygon_key', 'alpha_key')
        self.assertIsInstance(aggregator, AveragePriceAggregator)

    @patch('time.sleep', return_value=None)
    def test_add_stocks_to_portfolio(self, mock_sleep):
        portfolio = Portfolio('iex_token', 'polygon_key', 'alpha_key')
        aggregator = AveragePriceAggregator('iex_token', 'polygon_key', 'alpha_key')
        df = pd.DataFrame({'Ticker symbol': ['AAPL', 'MSFT'], 'Shares': [10, 20]})
        
        with patch.object(portfolio, 'add_stock') as mock_add_stock, \
             patch.object(aggregator, 'load_data', return_value={'AAPL': 100, 'MSFT': 200}):
            add_stocks_to_portfolio(portfolio, aggregator, df)
            mock_add_stock.assert_any_call('AAPL', 10)
            mock_add_stock.assert_any_call('MSFT', 20)
            self.assertEqual(mock_add_stock.call_count, 2)

    def test_prepare_stock_data_for_optimization(self):
        portfolio = Portfolio('iex_token', 'polygon_key', 'alpha_key')
        portfolio.stocks = {'AAPL': 10, 'MSFT': 20}
        aggregator = AveragePriceAggregator('iex_token', 'polygon_key', 'alpha_key')

        with patch.object(aggregator, 'load_data', return_value=[100, 200]) as mock_load_data:
            df_prices, stock_symbols = prepare_stock_data_for_optimization(portfolio, aggregator)
            self.assertEqual(stock_symbols, ['AAPL', 'MSFT'])
            self.assertIsInstance(df_prices, pd.DataFrame)

    def test_optimize_portfolio(self):
        df_prices = pd.DataFrame({'AAPL': [100, 101, 102], 'MSFT': [200, 201, 202]})
        optimizer = optimize_portfolio(df_prices)
        self.assertIsInstance(optimizer, PortfolioOptimizer)

    def test_calculate_actual_portfolio_risk_return(self):
        df = pd.DataFrame({'Ticker symbol': ['AAPL', 'MSFT'], 'Shares': [10, 20]})
        stock_symbols = ['AAPL', 'MSFT']
        optimizer = MagicMock()
        optimizer.calculate_portfolio_risk_return.return_value = (0.1, 0.2)
        
        risk = calculate_actual_portfolio_risk_return(optimizer, df, stock_symbols)
        self.assertEqual(risk, 0.1)

    @patch('src.portfolio.Portfolio')
    @patch('src.backtester.Backtester')
    def test_generate_and_backtest_portfolios(self, MockBacktester, MockPortfolio):
        optimizer = MagicMock()
        optimizer.generate_similar_risk_portfolios.return_value = [[0.5, 0.5], [0.6, 0.4]]
        portfolio = Portfolio('iex_token', 'polygon_key', 'alpha_key')
        stock_symbols = ['AAPL', 'MSFT']
        total_shares = 30
        tokens = {'IEX_TOKEN': 'iex_token', 'POLYGON_KEY': 'polygon_key', 'ALPHA_KEY': 'alpha_key'}

        generate_and_backtest_portfolios(optimizer, 0.1, portfolio, stock_symbols, total_shares, tokens)
        self.assertEqual(MockPortfolio.call_count, 2)
        self.assertEqual(MockBacktester.call_count, 2)

if __name__ == '__main__':
    unittest.main()