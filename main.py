import time
import os
import pandas as pd
from src.stock_data_loader import StockDataLoader
from src.portfolio import Portfolio
from src.average_price_aggregator import AveragePriceAggregator
from src.optimize import PortfolioOptimizer

def main():
    # Initialize the StockDataLoader and load stock positions from the CSV file
    data_loader = StockDataLoader('data/portfolio_positions.csv')
    df = data_loader.load_data()
    print(df)
    
    # Initialize the Portfolio
    iex_token = os.getenv('IEX_TOKEN')
    polygon_key = os.getenv('POLYGON_KEY')
    alpha_key = os.getenv('ALPHA_KEY')
    portfolio = Portfolio(iex_token, polygon_key, alpha_key)
    
    # Initialize the AveragePriceAggregator
    aggregator = AveragePriceAggregator(iex_token, polygon_key, alpha_key)
    
    # Add stocks to the portfolio
    for index, row in df.iterrows():
        stock_symbol = row['Ticker symbol']
        shares = row['Shares']
        portfolio.add_stock(stock_symbol, shares)
        print(f"Added {shares} shares of {stock_symbol} to the portfolio.")
        
        # Fetch and aggregate average price data
        average_prices = aggregator.load_data(stock_symbol)
        print(f"Average prices for {stock_symbol}:")
        print(average_prices)
        time.sleep(1)  # Delay to avoid hitting API rate limits

    # Print portfolio value
    print(f"Total portfolio value: {portfolio.get_portfolio_value()}")

    # Prepare stock data for optimization
    stock_symbols = list(portfolio.stocks.keys())
    price_data = {symbol: aggregator.load_data(symbol) for symbol in stock_symbols}
    
    # Convert price data to DataFrame
    df_prices = pd.DataFrame({symbol: pd.Series(data) for symbol, data in price_data.items()})
    
    # Initialize the PortfolioOptimizer
    optimizer = PortfolioOptimizer(df_prices)
    optimizer.calculate_efficient_frontier()
    optimizer.display_efficient_frontier()
    
    # Calculate and print risk/return for the actual portfolio
    actual_weights = [df.loc[df['Ticker symbol'] == symbol, 'Shares'].values[0] for symbol in stock_symbols]
    total_shares = sum(actual_weights)
    actual_weights = [weight / total_shares for weight in actual_weights]
    risk, return_ = optimizer.calculate_portfolio_risk_return(actual_weights)
    print(f"Actual portfolio risk: {risk}, return: {return_}")

if __name__ == "__main__":
    main()