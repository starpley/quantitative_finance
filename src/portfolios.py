import os
import json
from datetime import datetime
from collections import defaultdict
from yfinance import Ticker as YahooFinanceProvider
from iexfinance.stocks import Stock as IEXCloudProvider
from polygon import BaseClient as PolygonProvider
from alpha_vantage.timeseries import TimeSeries as AlphaVantageProvider

from src.portfolio import Portfolio

class Portfolio:
    
    current_portfolio = Portfolio()
    
    def __init__(self, porfolio_count):
        pass
    
    def create_random_portfolios(self, num_portfolios):
        pass
    
    def get_best_portfolios(self, target_risk, target_return, num_portfolios):
        pass    
    
    
    
    