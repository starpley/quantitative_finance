import time
import os
import json
import pandas as pd
from src.asset_data import StockDataLoader
from src.portfolio import Portfolio
from src.optimizer import Optimizer
from src.backtester import Backtester
from src.portfolios import Portfolio

def main():
    tokens = load_api_tokens()
    data_loader = StockDataLoader('data/portfolio_positions.csv')
    df = data_loader.load_data()
    print(df)

    portfolio = initialize_portfolio(tokens)
    if not portfolio.stocks:  # Check if portfolio is empty (JSON file didn't exist)
        add_stocks_to_portfolio(portfolio, df)
        portfolio.save_portfolio()  # Save the portfolio after adding stocks

    print(f"Total portfolio value: {portfolio.get_portfolio_value()}")

    df_prices, stock_symbols = prepare_stock_data_for_optimization(portfolio)
    optimizer = optimize_portfolio(df_prices)

    risk = calculate_actual_portfolio_risk_return(optimizer, df, stock_symbols)
    total_shares = sum(df['Shares'])

    generate_and_backtest_portfolios(optimizer, risk, portfolio, stock_symbols, total_shares, tokens)

if __name__ == "__main__":
    main()