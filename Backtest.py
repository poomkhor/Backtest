# packages to use numpy, pandas, scipy.optimize, streamlit
import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st

from scipy.optimize import brute

#init Backtesting Class
class Backtesting():
   
    '''
    ### Class for vectorized backtesting
    ======================================
    #### Methods
    --------------------------------------
    get_data:
        retrieve data from Yahoo Finance using yfinance
    MRStrat:
        Mean Reversion strategy data prep
    MOStrat:
        Momentum strategy data prep
    run_strat:
        Run strategy and plot data to be displayed in streamlit
    optimize:
        Strategy optimization using scipy.optimize
    '''
    def __init__(self, symbol, start, end, interval):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.interval = interval
        self.results = None

# processing incoming data for backtesting and generate daily return column
    def get_data(self):
        data = yf.download(self.symbol, self.start, self.end, self.interval)
        self.data = data.dropna().drop(columns=['Volume', 'Dividends', 'Stock Splits'])
        self.data['daily_r'] = np.log(self.data['Close']/self.data['Close'].shift(1))

# strategy to run 1) mean-reversion 2) momentum, this should produce strategy and position
    def MRStrat(self, SMA1=12, SMA2=60):
        self.SMA1 = SMA1
        self.SMA2 = SMA2
        # check if enough data to run the strategy
        if len(self.data.index) > self.SMA2:
            # if enough data start calculating SMA1 & SMA2
            self.data['SMA1'] = self.data['Close'].rolling(self.SMA1).mean()
            self.data['SMA2'] = self.data['Close'].rolling(self.SMA2).mean()
        else:
            print('not enough data for the strategy')

        self.data['position'] = np.where(self.data['SMA1'] > self.data['SMA2'], 1, -1)
        # self.data = data

    def MOStrat(self, momentum=1):
        '''position will equal to sign on direction of average return over the momentum period'''
        self.momentum = momentum
        # check if enough data for the strategy
        if len(self.data.index) > momentum:
            self.data['position'] = np.sign(self.data['daily_r'].rolling(self.momentum).mean())
        else:
            print('not enough data for the strategy')

# run strategy with cum_return, cum_strategy, drawdown then plot it with streamlit
    def run_strat(self):
        self.data['strategy'] = self.data['position'].shift(1) * self.data['daily_r']
        self.data.dropna(inplace=True)
        self.data['sum_daily'] = self.data['daily_r'].cumsum().apply(np.exp)
        self.data['sum_strat'] = self.data['strategy'].cumsum().apply(np.exp)
        # gross performance of the strategy
        performa = self.data['sum_strat'].iloc[-1].round(2)
        # out/underperform of strategy
        compare = performa - self.data['sum_daily'].iloc[-1].round(2)
        # check if self.results
        if 'SMA1' in self.data:
            # set up data for charting in streamlit
            stockdata = self.data[['Close', 'SMA1', 'SMA2']].copy()
        else:
            stockdata = self.data[['Close']].copy()
            perfdata = self.data[['sum_daily', 'sum_strat', 'position']]
            st.title('Strategy Results')
            st.write(f'The strategy has gross performance = {performa} out/underperform by {compare}')
            # 2 charts displaying
            st.line_chart(stockdata)
            st.line_chart(perfdata)

# optimize strategy using scipy
    def optimize(self):
        pass
# later can add max_dd, max_dd_duration, trade

if __name__ == '__main__':
    bt = Backtesting('MSFT', '2009-01-01', '2021-06-30', '1d')
    bt.get_data()
    '''Choose one of the 2 strategies below'''
    # bt.MRStrat()
    bt.MOStrat(momentum=60)
    bt.run_strat()

