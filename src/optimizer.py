import polars as pl
import numpy as np
import yfinance as yf
from scipy.optimize import minimize

class Optimizer:
    def __init__(self, portfolio):
        self.portfolio = portfolio

    def optimize_portfolio(self, desired_return):
        stock_symbols = list(self.portfolio.stocks.keys())
        num_assets = len(stock_symbols)

        # Fetch historical data for each stock
        returns = []
        for stock_symbol in stock_symbols:
            stock = yf.Ticker(stock_symbol)
            hist = stock.history(period="max")
            hist['Return'] = hist['Close'].pct_change()
            returns.append(hist['Return'][1:])
        
        returns_df = pl.DataFrame(returns).transpose()
        expected_returns = returns_df.mean()
        covariance_matrix = returns_df.cov()

        # Define the objective function (minimize variance)
        def objective(weights):
            return np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))

        # Constraints: Expected return should be equal to desired return
        constraints = ({'type': 'eq', 'fun': lambda weights: np.dot(weights, expected_returns) - desired_return},
                       {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})

        # Bounds: Weights should be between 0 and 1
        bounds = tuple((0, 1) for _ in range(num_assets))

        # Initial guess: Equal distribution
        initial_guess = num_assets * [1. / num_assets]

        # Run optimization
        optimized_result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

        # Calculate the amount to sell for each stock
        optimized_weights = optimized_result.x
        current_values = np.array([self.portfolio.stocks[symbol] * yf.Ticker(symbol).history(period='1d')['Close'].iloc[-1] for symbol in stock_symbols])
        target_values = optimized_weights * self.portfolio.get_portfolio_value()

        sell_amounts = current_values - target_values
        return dict(zip(stock_symbols, sell_amounts))

    def calculate_portfolio_risk(self):
        stock_symbols = list(self.portfolio.stocks.keys())
        num_assets = len(stock_symbols)

        # Fetch historical data for each stock
        returns = []
        for stock_symbol in stock_symbols:
            stock = yf.Ticker(stock_symbol)
            hist = stock.history(period="max")
            hist['Return'] = hist['Close'].pct_change()
            returns.append(hist['Return'][1:])
        
        returns_df = pl.DataFrame(returns).transpose()
        covariance_matrix = returns_df.cov()

        # Calculate portfolio risk (standard deviation)
        weights = np.array([self.portfolio.stocks[symbol] for symbol in stock_symbols])
        weights = weights / np.sum(weights)
        portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
        portfolio_risk = np.sqrt(portfolio_variance)
        return portfolio_risk