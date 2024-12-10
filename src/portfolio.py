import os
import json
from datetime import datetime
from collections import defaultdict
from yfinance import Ticker as YahooFinanceProvider
from iexfinance.stocks import Stock as IEXCloudProvider
from polygon import BaseClient as PolygonProvider
from alpha_vantage.timeseries import TimeSeries as AlphaVantageProvider

from src.asset_data import AssetData

class Portfolio:
    
    asset_data = None
    
    def __init__(self):
        pass
    
    def create_portfolio(self, stock_positions):
        pass
    
    def create_random_portfolio(self):
        pass
    
    def calculate_portfolio_risk_return(self):
        pass
    
    def calculate_portfolio_sharpe_ratio(self):
        pass
    
    