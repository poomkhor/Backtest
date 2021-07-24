# packages to use numpy, pandas, scipy.optimize, streamlit
import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import copy

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
        # cloned_output = copy.deepcopy(self.get_data(self))
# processing incoming data for backtesting and generate daily return column
    # @st.cache(allow_output_mutation=True)
    def get_data(self):
        raw = yf.download(self.symbol, self.start, self.end, self.interval)
        self.raw = raw.dropna().drop(columns=['Volume', 'Dividends', 'Stock Splits'])
        self.raw['daily_r'] = np.log(self.raw['Close']/self.raw['Close'].shift(1))
        self.raw1 = copy.deepcopy(raw)
        return self.raw

# strategy to run 1) mean-reversion 2) momentum, this should produce strategy and position
    def MRStrat(self, SMA1=10, SMA2=20):
        self.data = self.raw.copy()
        self.SMA1 = SMA1
        self.SMA2 = SMA2
        # self.MRStrat = 1
        # check if enough data to run the strategy    
        self.data['SMA1'] = self.data['Close'].rolling(self.SMA1).mean()    
        self.data['SMA2'] = self.data['Close'].rolling(self.SMA2).mean()
        self.data['position'] = np.where(self.data['SMA1'] > self.data['SMA2'], 1, -1)  
        return self.data

    def MOStrat(self, momentum=1):
        '''position will equal to sign on direction of average return over the momentum period'''
        self.data = self.data.copy()
        self.momentum = momentum
        self.MOStrat = 1
        # check if enough data for the strategy
        if len(self.data.index) > momentum:
            self.data['position'] = np.sign(self.data['daily_r'].rolling(self.momentum).mean())
        else:
            print('not enough data for the strategy')
        return self.data

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
        # custom streamlit webapp to present the data
        header = st.beta_container()
        dataset = st.beta_container()
        strategy = st.beta_container()

        SMA1 = st.sidebar.slider('SMA1', min_value=10, max_value=90, value=20, step=10)
        SMA2 = st.sidebar.slider('SMA2', min_value=50, max_value=200, value=60, step=10)

        with header:
            st.title('Stock Trading Strategy Backtesting')
            st.write('This project is to demonstrate a simple stock strategies backtesting in streamlit')

        with dataset:
            st.write(f'Below is the data of stock : {self.symbol}')
            st.dataframe(self.data)

        with strategy:
            st.header('Strategy Results')
            st.write(f'The strategy has gross performance = {performa} out/underperform by {compare}')
            # 2 charts displaying
            st.line_chart(stockdata)
            st.line_chart(perfdata)
            return performa
# need another function to optimize
    def run_update(self, SMA):
        self.MRStrat(int(SMA[0]), int(SMA[1]))
        return -self.run_strat()
# optimize strategy using scipy
    def optimize(self, SMA1_range, SMA2_range):
        '''find optimum parameter for strategies based on given parameter range'''
        # pass
        # if self.MRStrat == 1:
        opt = brute(self.run_update, (SMA1_range, SMA2_range), finish=None)
        return opt, self.run_update(opt)

# later can add max_dd, max_dd_duration, trade

if __name__ == '__main__':
    bt = Backtesting('MSFT', '2009-01-01', '2021-06-30', '1d')
    bt.get_data()
    # '''Choose one of the 2 strategies below'''
    bt.MRStrat(SMA1=10, SMA2=20)
    # bt.MOStrat(momentum=60)
    bt.run_strat()
    # print(bt.optimize((30,56, 4), (150,250,4)))

