import numpy as np
import polars as pl
from src.asset_data import AssetData

class Portfolio:
    # Static member variable for AssetData
    asset_data = None

    def __init__(self, file_path, risk_free_rate=0.01, start_date='2020-01-01', end_date='2023-01-01'):
        if Portfolio.asset_data is None:
            Portfolio.asset_data = AssetData(file_path)
        self.portfolio = []
        self.risk_free_rate = risk_free_rate
        self.start_date = start_date
        self.end_date = end_date
        self.estimated_return = None
        self.estimated_risk = None
        self.sharpe_ratio = None

    def create_portfolio(self, stock_positions):
        total_quantity = sum(quantity for _, quantity in stock_positions)
        self.portfolio = [(stock, quantity / total_quantity * 100) for stock, quantity in stock_positions]
        self._calculate_portfolio_metrics()

    def create_random_portfolio(self, num_stocks=10):
        import random
        all_stocks = Portfolio.asset_data.data['Ticker symbol'].to_list()
        selected_stocks = random.sample(all_stocks, num_stocks)
        stock_positions = [(stock, random.randint(1, 100)) for stock in selected_stocks]
        self.create_portfolio(stock_positions)

    def create_portfolio_from_holdings(self):
        holdings = Portfolio.asset_data.get_holdings()
        self.create_portfolio(holdings)

    def _normalize_portfolio(self):
        total_percentage = sum(percentage for _, percentage in self.portfolio)
        self.portfolio = [(stock, percentage / total_percentage * 100) for stock, percentage in self.portfolio]

    def _calculate_portfolio_metrics(self):
        returns = []
        weights = []
        for stock, percentage in self.portfolio:
            history = Portfolio.asset_data.get_stock_history(stock, self.start_date, self.end_date)
            stock_returns = history['Close'].pct_change().dropna().to_pandas()
            returns.append(stock_returns)
            weights.append(percentage / 100)

        returns_df = pl.DataFrame(np.column_stack(returns), columns=[stock for stock, _ in self.portfolio])

        mean_returns = returns_df.mean(axis=0).to_numpy() * 252
        cov_matrix = returns_df.cov().to_numpy() * 252

        self.estimated_return = np.dot(weights, mean_returns)
        portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
        self.estimated_risk = np.sqrt(portfolio_variance)
        self.sharpe_ratio = (self.estimated_return - self.risk_free_rate) / self.estimated_risk

    def calculate_portfolio_risk_return(self):
        return self.estimated_return, self.estimated_risk

    def calculate_portfolio_sharpe_ratio(self):
        return self.sharpe_ratio
    
    def display_portfolio_metrics(self, portfolio_value=None):
        if portfolio_value is None:
            # Use default value from AssetData if not provided
            portfolio_value = sum([quantity * self.asset_data.get_stock_price(ticker) for ticker, quantity in self.holdings])
        
        portfolio_return, portfolio_risk = self.calculate_portfolio_risk_return()
        sharpe_ratio = self.calculate_portfolio_sharpe_ratio()
        
        print("Portfolio Metrics:")
        print(f"Total Portfolio Value: ${portfolio_value:,.2f}")
        print(f"Portfolio Return: {portfolio_return:.2%}")
        print(f"Portfolio Risk: {portfolio_risk:.2%}")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        
        print("\nHoldings:")
        for ticker, quantity in self.holdings:
            stock_name = self.asset_data.get_stock_name(ticker)
            print(f"Stock: {stock_name} (Ticker: {ticker}), Shares: {quantity:.2f}")
