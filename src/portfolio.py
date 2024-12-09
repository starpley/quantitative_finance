from quote_providers import YahooFinanceProvider, IEXCloudProvider, PolygonProvider, AlphaVantageProvider

class Portfolio:
    def __init__(self, iex_token, polygon_key, alpha_key):
        self.stocks = {}
        self.yahoo_provider = YahooFinanceProvider()
        self.iex_provider = IEXCloudProvider(iex_token)
        self.polygon_provider = PolygonProvider(polygon_key)
        self.alpha_provider = AlphaVantageProvider(alpha_key)

    def add_stock(self, stock_symbol, shares):
        self.stocks[stock_symbol] = shares

    def remove_stock(self, stock_symbol):
        if stock_symbol in self.stocks:
            del self.stocks[stock_symbol]

    def get_stock_price(self, stock_symbol):
        # Try to get the quote from different providers in order
        try:
            return self.yahoo_provider.get_quote(stock_symbol)
        except Exception as e:
            print(f"Yahoo Finance error: {e}")
        
        try:
            return self.iex_provider.get_quote(stock_symbol)
        except Exception as e:
            print(f"IEX Cloud error: {e}")
        
        try:
            return self.polygon_provider.get_quote(stock_symbol)
        except Exception as e:
            print(f"Polygon.io error: {e}")
        
        try:
            return self.alpha_provider.get_quote(stock_symbol)
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
        
        raise Exception("All providers failed to get the stock price")

    def get_portfolio_value(self):
        total_value = 0
        for stock_symbol, shares in self.stocks.items():
            current_price = self.get_stock_price(stock_symbol)
            total_value += shares * current_price
        return total_value