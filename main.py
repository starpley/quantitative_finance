
from src.asset_data import AssetData
from src.portfolios import Portfolios

def main():
    # Create AssetData instance
    asset_data = AssetData('data/portfolio_positions.csv')
    
    # Create Portfolios instance
    portfolios = Portfolios(asset_data, portfolio_count=10)
    
    # Create portfolio from holdings
    current_portfolio = portfolios.create_portfolio_from_holdings()
    
    # Create ten random portfolios
    portfolios.create_random_portfolios(10)
    
    # Print the current portfolio and random portfolios
    print("Current Portfolio:")
    print(current_portfolio)
    
    print("Random Portfolios:")
    for portfolio in portfolios.portfolios:
        print(portfolio)
    
    # Plot the efficient frontier chart
    target_return = 0.08  # Example target return
    portfolios.plot_efficient_frontier(target_return, file_path='efficient_frontier.png')
    print("Efficient frontier chart saved as 'efficient_frontier.png'.")

if __name__ == "__main__":
    main()