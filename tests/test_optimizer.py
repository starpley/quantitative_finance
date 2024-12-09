import unittest
from src.portfolio import Portfolio
from src.optimizer import Optimizer

class TestOptimizer(unittest.TestCase):
    def setUp(self):
        self.portfolio = Portfolio()
        self.portfolio.add_stock('AAPL', 100)
        self.portfolio.add_stock('GOOG', 50)
        self.portfolio.add_stock('MSFT', 200)
        self.portfolio.add_stock('TSLA', 75)
        self.optimizer = Optimizer(self.portfolio)

    def test_optimize_portfolio(self):
        desired_return = 0.1  # Example desired return
        sell_amounts = self.optimizer.optimize_portfolio(desired_return)
        self.assertEqual(len(sell_amounts), 4)

    def test_calculate_portfolio_risk(self):
        risk = self.optimizer.calculate_portfolio_risk()
        self.assertGreater(risk, 0)

if __name__ == '__main__':
    unittest.main()