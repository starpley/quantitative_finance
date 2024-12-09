import time
from src.stock_data_loader import StockDataLoader
from src.portfolio import Portfolio
from src.optimizer import Optimizer
from src.backtester import Backtester

def main():
    data_loader = StockDataLoader('data/portfolio_positions.csv')
    df = data_loader.load_data()
    print(df)
    
    portfolio = Portfolio()
    optimizer = Optimizer(portfolio)
    backtester = Backtester(portfolio)

    for index, row in df.iterrows():
        stock_symbol = row['symbol']
        shares = row['shares']
        portfolio.add_stock(stock_symbol, shares)
        print(f"Added {shares} shares of {stock_symbol} to the portfolio.")
        time.sleep(60)  # Delay for one minute

    optimizer.optimize_portfolio(0.1)
    backtester.backtest_portfolio('2023-01-01', '2023-12-31')

if __name__ == "__main__":
    main()