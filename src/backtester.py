import yfinance as yf
import polars as pl
import numpy as np
class Backtester:
    def __init__(self, portfolio):
        self.portfolio = portfolio
    def backtest_portfolio(self):
        stock_symbols = list(self.portfolio.stocks.keys())
        historical_data = {}
        # Fetch maximum available historical data for each stock
        for stock_symbol in stock_symbols:
            stock = yf.Ticker(stock_symbol)
            hist = stock.history(period="max")
            historical_data[stock_symbol] = hist['Close']
        historical_data_df = pl.DataFrame(historical_data)
        self.historical_data_df = historical_data_df
        return historical_data_df
    def calculate_performance(self):
        stock_symbols = list(self.portfolio.stocks.keys())
        shares = np.array([self.portfolio.stocks[symbol] for symbol in stock_symbols])
        initial_prices = self.historical_data_df[0]
        final_prices = self.historical_data_df[-1]
        initial_value = np.sum(initial_prices * shares)
        final_value = np.sum(final_prices * shares)
        performance = (final_value - initial_value) / initial_value
        return performance
# Example usage:
# portfolio = Portfolio()
# portfolio.add_stock('AAPL', 100)
# portfolio.add_stock('GOOG', 50)
# portfolio.add_stock('MSFT', 200)
# portfolio.add_stock('TSLA', 75)
# backtester = Backtester(portfolio)
# backtester.backtest_portfolio()
# performance = backtester.calculate_performance()
# print(f'Portfolio performance: {performance:.2%}')