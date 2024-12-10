import numpy as np
import matplotlib.pyplot as plt
from src.portfolio import Portfolio

class Portfolios:
    def __init__(self, asset_data):
        self.asset_data = asset_data
        self.portfolios = None
        self.current_portfolio = None
        self.best_portfolios_by_return = []

    def create_random_portfolios(self, num_portfolios):
        self.portfolios = [Portfolio(self.asset_data) for _ in range(num_portfolios)]
        for portfolio in self.portfolios:
            portfolio.create_random_portfolio()

    def create_portfolio_from_holdings(self):
        holdings = self.asset_data.get_holdings()
        self.current_portfolio = Portfolio(self.asset_data)
        self.current_portfolio.create_portfolio(holdings)
        return self.current_portfolio

    def get_best_portfolios_by_risk(self, target_risk, num_portfolios):
        return sorted(
            self.portfolios, key=lambda p: abs(p.estimated_risk - target_risk)
        )[:num_portfolios]

    def get_best_portfolios_by_return(self, target_return, num_portfolios):
        # Find portfolios with the desired return and sort them by the lowest risk
        filtered_portfolios = [p for p in self.portfolios if abs(p.estimated_return - target_return) < 0.01]  # Adjust the threshold as needed
        self.best_portfolios_by_return = sorted(
            filtered_portfolios, key=lambda p: p.estimated_risk
        )[:num_portfolios]
        return self.best_portfolios_by_return

    def plot_efficient_frontier(self, target_return=None, file_path='efficient_frontier.png'):
        risks = []
        returns = []
        for portfolio in self.portfolios:
            est_return, est_risk = portfolio.calculate_portfolio_risk_return()
            risks.append(est_risk)
            returns.append(est_return)

        plt.figure(figsize=(10, 6))
        plt.scatter(risks, returns, c=(np.array(returns) - self.asset_data.risk_free_rate) / np.array(risks), marker='o', label='Random Portfolios')

        if self.current_portfolio:
            est_return, est_risk = self.current_portfolio.calculate_portfolio_risk_return()
            plt.scatter([est_risk], [est_return], color='red', marker='*', s=200, label='Current Portfolio')

        # Highlight best portfolios by return if target_return is provided
        if target_return is not None:
            self.get_best_portfolios_by_return(target_return, 5)

        if self.best_portfolios_by_return:
            best_risks = [p.estimated_risk for p in self.best_portfolios_by_return]
            best_returns = [p.estimated_return for p in self.best_portfolios_by_return]
            plt.scatter(best_risks, best_returns, color='orange', marker='X', s=100, label='Best Portfolios by Return')

        plt.xlabel('Risk (Standard Deviation)')
        plt.ylabel('Return')
        plt.colorbar(label='Sharpe Ratio')
        plt.title('Efficient Frontier')
        plt.legend()
        plt.savefig(file_path)
        plt.close()

# Example usage:
# asset_data = AssetData('path_to_data_file.csv')
# portfolios = Portfolios(asset_data, portfolio_count=100)
# portfolios.create_random_portfolios(100)
# portfolios.create_portfolio_from_holdings()
# portfolios.plot_efficient_frontier(target_return=0.08, file_path='efficient_frontier.png')