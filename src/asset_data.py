import polars as pl
import yfinance as yf

class AssetData :
    def __init__(self, file_path):
        self.file_path = file_path
        self.portfolio = self.load_data()

    def load_data(self):
        df = pl.read_csv(self.file_path)
        return df

    def get_stock_history(self, ticker_symbol, start_date, end_date):
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(start=start_date, end=end_date)
        return pl.DataFrame(hist)

    def update_current_prices(self):
        for row in self.portfolio.iter_rows(named=True):
            ticker_symbol = row['Ticker symbol']
            stock = yf.Ticker(ticker_symbol)
            current_price = stock.history(period='1d')['Close'].iloc[-1]
            self.portfolio = self.portfolio.with_column(
                pl.Series(
                    (self.portfolio['Ticker symbol'] == ticker_symbol).map(lambda x: current_price if x else row['Current price']),
                    name='Current price'
                )
            )
        return self.portfolio