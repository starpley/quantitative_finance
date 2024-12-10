from datetime import datetime, timedelta
from loguru import logger
from src.asset_data import AssetData
from src.portfolios import Portfolios

def main():
    logger.info("Starting the main function")
    
    # Create AssetData instance
    logger.info("Creating AssetData instance")
    asset_data = AssetData('data/portfolio_positions.csv')

    # Define date range for 20 years
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=20*365)).strftime('%Y-%m-%d')
    logger.info(f"Date range defined: Start Date - {start_date}, End Date - {end_date}")
    
    # Fetch stock histories for all holdings
    logger.info("Fetching stock histories for all holdings")
    stock_histories = asset_data.fetch_all_stock_histories(start_date, end_date)
    
    # Check if stock histories were fetched successfully
    if stock_histories:
        logger.info("Stock histories fetched successfully")
    else:
        logger.warning("No stock histories found")

    # Create Portfolios instance
    logger.info("Creating Portfolios instance")
    portfolios = Portfolios(asset_data)
    
    # Create portfolio from holdings
    logger.info("Creating portfolio from holdings")
    current_portfolio = portfolios.create_portfolio_from_holdings()
    
    # Create ten random portfolios
    logger.info("Creating ten random portfolios")
    portfolios.create_random_portfolios(10)
    
    # Print the current portfolio and random portfolios
    logger.info("Printing the current portfolio and random portfolios")
    print("Current Portfolio:")
    print(current_portfolio)
    
    print("Random Portfolios:")
    for portfolio in portfolios.portfolios:
        print(portfolio)
    
    # Plot the efficient frontier chart
    target_return = 0.08  # Example target return
    logger.info(f"Plotting the efficient frontier chart with target return: {target_return}")
    portfolios.plot_efficient_frontier(target_return, file_path='efficient_frontier.png')
    logger.info("Efficient frontier chart saved as 'efficient_frontier.png'.")

if __name__ == "__main__":
    main()