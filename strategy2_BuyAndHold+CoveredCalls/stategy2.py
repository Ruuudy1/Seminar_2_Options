# region imports
from AlgorithmImports import *
# endregion

class SleepyOrangeTapir(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2007, 1, 1)  # Start date
        self.SetEndDate(2024, 10, 7)    # End date for backtest (40 years) ** OPTIONS DATA ONLY SPANS TO 2007 (17 years)
        self.SetCash(100000)            # Starting cash
        self.spy = self.AddEquity("SPY", Resolution.Minute).Symbol
        
        # Add SPY options
        option = self.AddOption("SPY")
        option.SetFilter(-10, 10, timedelta(30), timedelta(60))  # Filter for options expiring 30 to 60 days out
        
        self.next_call_date = self.StartDate + timedelta(days=30)  # Track the date of the next covered call sale

    def OnData(self, data):
        # Buy exactly 100 shares initially
        if not self.Portfolio[self.spy].Invested:
            self.MarketOrder(self.spy, 100)  # Buy exactly 100 shares of SPY
        
        # Sell covered calls on the specified date (monthly)
        if self.Time >= self.next_call_date:
            self.SellCoveredCalls(data)
            self.next_call_date += timedelta(days=30)  # Update next call date for the following month

    def SellCoveredCalls(self, data):
        # Get number of SPY shares and determine how many covered calls to sell
        spy_shares = self.Portfolio[self.spy].Quantity
        num_calls = spy_shares // 100  # Number of covered calls to sell
        
        # Access option chain data
        if self.spy in data.OptionChains:
            option_chain = data.OptionChains[self.spy]
            
            # Get call options expiring in 30 days with delta <= 0.25
            contracts = [contract for contract in option_chain if contract.Expiry == self.Time + timedelta(days=30)]
            call_contracts = sorted([contract for contract in contracts if contract.Right == OptionRight.Call and contract.Greeks.Delta <= 0.25], 
                                     key=lambda x: x.Strike)
            
            # Sell covered calls based on number of SPY shares owned
            if call_contracts:
                call_to_sell = call_contracts[0]
                self.SellOptionContract(call_to_sell, num_calls)  # Sell covered calls (num_calls contracts)

    def OnOrderEvent(self, order_event):
        # When an option expires or is assigned, reinvest the premium into buying more SPY shares
        if order_event.Status == OrderStatus.Filled and order_event.Symbol.SecurityType == SecurityType.Option:
            premium_received = order_event.FillPrice * order_event.FillQuantity  # Calculate premium received
            num_shares_to_buy = premium_received // self.Securities[self.spy].Price  # Determine how many SPY shares to buy
            if num_shares_to_buy > 0:
                self.MarketOrder(self.spy, int(num_shares_to_buy))  # Reinvest premium into SPY shares
