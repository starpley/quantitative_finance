import numpy as np
import polars as pl
from loguru import logger
from src.asset_data import AssetData

class Portfolio:
    # Static member variable for AssetData
    asset_data = None

    def __init__(self, asset_data, risk_free_rate=0.01, start_date='2020-01-01', end_date='2023-01-01'):
        if Portfolio.asset_data is None:
            Portfolio.asset_data = asset_data
        self.portfolio = []
        self.risk_free_rate = risk_free_rate
        self.start_date = start_date
        self.end_date = end_date
        self.estimated_return = None
        self.estimated_risk = None
        self.sharpe_ratio = None
        logger.info(f"Initialized Portfolio with start_date: {self.start_date}, end_date: {self.end_date}, risk_free_rate: {self.risk_free_rate}")

    def create_portfolio(self, stock_positions):
        total_quantity = sum(quantity for _, _, quantity in stock_positions)
        self.portfolio = [(stock, quantity / total_quantity * 100) for _, stock, quantity in stock_positions]
        logger.info(f"Created portfolio with stocks: {self.portfolio}")
        self._calculate_portfolio_metrics()

    def create_random_portfolio(self, num_stocks=10):
        import random
        all_stocks = Portfolio.asset_data.data['Ticker symbol'].to_list()
        selected_stocks = random.sample(all_stocks, num_stocks)
        stock_positions = [(stock, random.randint(1, 100)) for stock in selected_stocks]
        logger.info(f"Selected random stocks for portfolio: {selected_stocks}")
        self.create_portfolio(stock_positions)

    def create_portfolio_from_holdings(self):
        holdings = Portfolio.asset_data.get_holdings()
        stock_positions = [(ticker, shares_owned) for _, ticker, shares_owned in holdings]
        self.create_portfolio(stock_positions)

    def _normalize_portfolio(self):
        total_percentage = sum(percentage for _, percentage in self.portfolio)
        self.portfolio = [(stock, percentage / total_percentage * 100) for stock, percentage in self.portfolio]
        logger.debug(f"Normalized portfolio: {self.portfolio}")

    def _calculate_portfolio_metrics(self):
        logger.info("Starting portfolio metrics calculation")
        returns = []
        weights = []
        
        try:
            for stock, percentage in self.portfolio:
                logger.debug(f"Processing stock: {stock}, percentage: {percentage}")
                try:
                    history = Portfolio.asset_data.get_stock_history(stock, self.start_date, self.end_date)
                    if history is None or history.empty:
                        logger.warning(f"No history data found for stock: {stock}")
                        continue
                    if 'Close' not in history.columns:
                        logger.error(f"'Close' column missing in history data for stock: {stock}")
                        continue
                    
                    logger.debug(f"History data for stock {stock}: {history['Close'].head()}")
                    stock_returns = history['Close'].pct_change().dropna().to_pandas()
                    if stock_returns.empty:
                        logger.warning(f"No valid stock returns data for stock: {stock}")
                        continue

                    logger.debug(f"Stock returns for stock {stock}: {stock_returns.head()}")
                    
                    logger.debug("Stock returns calculated")
                    returns.append(stock_returns)
                    weights.append(percentage / 100)
                except Exception as e:
                    logger.error(f"Error fetching or processing stock history for {stock}: {e}")
                    raise

            logger.debug("Stock returns and weights calculated")

            returns_df = pl.DataFrame(np.column_stack(returns), columns=[stock for stock, _ in self.portfolio])
            logger.debug("Returns DataFrame created")

            mean_returns = returns_df.mean(axis=0).to_numpy() * 252
            cov_matrix = returns_df.cov().to_numpy() * 252
            logger.debug("Mean returns and covariance matrix calculated")

            self.estimated_return = np.dot(weights, mean_returns)
            portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
            self.estimated_risk = np.sqrt(portfolio_variance)
            self.sharpe_ratio = (self.estimated_return - self.risk_free_rate) / self.estimated_risk
            logger.info(f"Calculated portfolio metrics: return={self.estimated_return}, risk={self.estimated_risk}, sharpe_ratio={self.sharpe_ratio}")
        
        except Exception as e:
            logger.error(f"Error in calculating portfolio metrics: {e}")
            raise
    def calculate_portfolio_risk_return(self):
        logger.info(f"Calculated portfolio risk and return: return={self.estimated_return}, risk={self.estimated_risk}")
        return self.estimated_return, self.estimated_risk

    def calculate_portfolio_sharpe_ratio(self):
        logger.info(f"Calculated portfolio Sharpe ratio: {self.sharpe_ratio}")
        return self.sharpe_ratio
    
    def display_portfolio_metrics(self, portfolio_value=None):
        if portfolio_value is None:
            # Use default value from AssetData if not provided
            portfolio_value = sum([quantity * self.asset_data.get_stock_price(ticker) for ticker, quantity in self.holdings])
        
        portfolio_return, portfolio_risk = self.calculate_portfolio_risk_return()
        sharpe_ratio = self.calculate_portfolio_sharpe_ratio()
        
        logger.info("Displaying portfolio metrics")
        print("Portfolio Metrics:")
        print(f"Total Portfolio Value: ${portfolio_value:,.2f}")
        print(f"Portfolio Return: {portfolio_return:.2%}")
        print(f"Portfolio Risk: {portfolio_risk:.2%}")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        
        print("\nHoldings:")
        for ticker, quantity in self.holdings:
            stock_name = self.asset_data.get_stock_name(ticker)
            print(f"Stock: {stock_name} (Ticker: {ticker}), Shares: {quantity:.2f}")