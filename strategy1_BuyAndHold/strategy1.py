# region imports
from AlgorithmImports import *
# endregion

class SleepyOrangeTapir(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2007, 1, 1) # QUANTCONNECT DATA ONLY GOES BACK TO 36 YEARS (1988)
        self.set_end_date(2024, 10, 7)   ### ONLY 17 YEAR BACKTEST SINCE OPTIONS ONLY GO BACK TO 2007
        self.set_cash(100000)
        self.add_equity("SPY", Resolution.MINUTE)

    def on_data(self, data: Slice):
        if not self.Portfolio.Invested:
            self.order("SPY", 100)  # Buy 100 shares of SPY