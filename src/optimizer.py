import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

class PortfolioOptimizer:
    def __init__(self, stock_data):
        self.stock_data = stock_data
        self.returns = self.stock_data.pct_change().dropna()
        self.mean_returns = self.returns.mean()
        self.cov_matrix = self.returns.cov()
        self.num_stocks = len(self.stock_data.columns)
        self.results = None

    def calculate_efficient_frontier(self, num_portfolios=10000):
        results = np.zeros((3, num_portfolios))
        for i in range(num_portfolios):
            weights = np.random.random(self.num_stocks)
            weights /= np.sum(weights)
            portfolio_return = np.sum(weights * self.mean_returns)
            portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            results[0,i] = portfolio_stddev
            results[1,i] = portfolio_return
            results[2,i] = portfolio_return / portfolio_stddev
        self.results = results

    def calculate_portfolio_risk_return(self, weights):
        portfolio_return = np.sum(weights * self.mean_returns)
        portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        return portfolio_stddev, portfolio_return

    def display_efficient_frontier(self):
        if self.results is None:
            raise ValueError("Efficient frontier not calculated. Call calculate_efficient_frontier first.")
        plt.scatter(self.results[0,:], self.results[1,:], c=self.results[2,:], cmap='YlGnBu', marker='o')
        plt.title('Efficient Frontier')
        plt.xlabel('Risk')
        plt.ylabel('Return')
        plt.colorbar(label='Sharpe ratio')
        plt.show()

# Example Usage
if __name__ == "__main__":
    # Mock data
    dates = pd.date_range('2023-01-01', '2024-01-01')
    stock_data = pd.DataFrame(np.random.randn(len(dates), 4), index=dates, columns=['AAPL', 'GOOGL', 'MSFT', 'AMZN'])

    optimizer = PortfolioOptimizer(stock_data)
    optimizer.calculate_efficient_frontier()
    optimizer.display_efficient_frontier()

    # Calculate risk/return for a specific portfolio
    weights = np.array([0.25, 0.25, 0.25, 0.25])
    risk, return_ = optimizer.calculate_portfolio_risk_return(weights)
    print(f"Portfolio Risk: {risk}, Portfolio Return: {return_}")