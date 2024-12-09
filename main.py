import time
import os
import json
import pandas as pd
from src.stock_data_loader import StockDataLoader
from src.portfolio import Portfolio
from src.average_price_aggregator import AveragePriceAggregator
from src.optimizer import Optimizer, PortfolioOptimizer
from src.backtester import Backtester

def load_api_tokens():
    with open('data/api_tokens.json', 'r') as f:
        return json.load(f)

def initialize_portfolio(tokens):
    return Portfolio(tokens['IEX_TOKEN'], tokens['POLYGON_KEY'], tokens['ALPHA_KEY'])

def initialize_aggregator(tokens):
    return AveragePriceAggregator(tokens['IEX_TOKEN'], tokens['POLYGON_KEY'], tokens['ALPHA_KEY'])

def add_stocks_to_portfolio(portfolio, aggregator, df):
    for index, row in df.iterrows():
        stock_symbol = row['Ticker symbol']
        shares = row['Shares']
        portfolio.add_stock(stock_symbol, shares)
        print(f"Added {shares} shares of {stock_symbol} to the portfolio.")

        average_prices = aggregator.load_data(stock_symbol)
        print(f"Average prices for {stock_symbol}:")
        print(average_prices)
        time.sleep(1)  # Delay to avoid hitting API rate limits

def prepare_stock_data_for_optimization(portfolio, aggregator):
    stock_symbols = list(portfolio.stocks.keys())
    price_data = {symbol: aggregator.load_data(symbol) for symbol in stock_symbols}
    df_prices = pd.DataFrame({symbol: pd.Series(data) for symbol, data in price_data.items()})
    return df_prices, stock_symbols

def optimize_portfolio(df_prices):
    optimizer = PortfolioOptimizer(df_prices)
    optimizer.calculate_efficient_frontier()
    optimizer.display_efficient_frontier()
    return optimizer

def calculate_actual_portfolio_risk_return(optimizer, df, stock_symbols):
    actual_weights = [df.loc[df['Ticker symbol'] == symbol, 'Shares'].values[0] for symbol in stock_symbols]
    total_shares = sum(actual_weights)
    actual_weights = [weight / total_shares for weight in actual_weights]
    risk, return_ = optimizer.calculate_portfolio_risk_return(actual_weights)
    print(f"Actual portfolio risk: {risk}, return: {return_}")
    return risk

def generate_and_backtest_portfolios(optimizer, risk, portfolio, stock_symbols, total_shares, tokens):
    similar_risk_portfolios = optimizer.generate_similar_risk_portfolios(risk, num_portfolios=10)
    print("Generated portfolios with similar risks:")
    for i, portfolio_weights in enumerate(similar_risk_portfolios):
        print(f"Portfolio {i + 1}: {portfolio_weights}")

    performances = []
    for i, portfolio_weights in enumerate(similar_risk_portfolios):
        test_portfolio = Portfolio(tokens['IEX_TOKEN'], tokens['POLYGON_KEY'], tokens['ALPHA_KEY'])
        for j, stock_symbol in enumerate(stock_symbols):
            shares = portfolio_weights[j] * total_shares
            test_portfolio.add_stock(stock_symbol, shares)
        backtester = Backtester(test_portfolio)
        backtester.backtest_portfolio()
        performance = backtester.calculate_performance()
        performances.append((i + 1, performance))
        print(f"Portfolio {i + 1} performance: {performance:.2%}")

    performances.sort(key=lambda x: x[1], reverse=True)
    print("Portfolios ranked by performance:")
    for rank, (portfolio_id, performance) in enumerate(performances, start=1):
        print(f"Rank {rank}: Portfolio {portfolio_id} with performance {performance:.2%}")

def main():
    tokens = load_api_tokens()
    data_loader = StockDataLoader('data/portfolio_positions.csv')
    df = data_loader.load_data()
    print(df)

    portfolio = initialize_portfolio(tokens)
    aggregator = initialize_aggregator(tokens)
    add_stocks_to_portfolio(portfolio, aggregator, df)

    print(f"Total portfolio value: {portfolio.get_portfolio_value()}")

    df_prices, stock_symbols = prepare_stock_data_for_optimization(portfolio, aggregator)
    optimizer = optimize_portfolio(df_prices)

    risk = calculate_actual_portfolio_risk_return(optimizer, df, stock_symbols)
    total_shares = sum(df['Shares'])

    generate_and_backtest_portfolios(optimizer, risk, portfolio, stock_symbols, total_shares, tokens)

if __name__ == "__main__":
    main()