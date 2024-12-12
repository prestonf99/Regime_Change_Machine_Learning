import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import matplotlib.patheffects as PathEffects
plt.style.use('dark_background')
plt.rcParams['axes.facecolor'] = '0.05'
plt.rcParams['grid.color'] = '0.15'

class Markov():
    def __init__(self, days, underlying):
        self.days = days
        self.underlying = underlying
        self.data = pd.DataFrame()
        if self.underlying == '^GSPC':
            self.symbol = 'SPX'
        elif self.underlying == '^NDX':
            self.symbol = 'NDX'
    def get_data(self):
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=self.days)
        ticker = yf.Ticker(self.underlying)
        self.data = ticker.history(interval='1d', start=self.start_date,
                                   end=self.end_date)
        self.data.index = self.data.index.date
        get_data = self.data
        get_data = get_data.drop(['Dividends', 'Volume', 'Stock Splits'], axis=1)
        get_data['Returns'] = np.log(get_data['Close'] /
                                     get_data['Close'].shift(1))
        get_data.dropna(inplace=True)
        return get_data
        
    def atr(self):
        self.atr_data = self.data
        self.atr_data = self.data.drop(['Dividends', 'Open', 'Close', 
                                  'Volume', 'Stock Splits'], axis=1)
        self.atr_data['RNG'] = self.atr_data['High'] - self.atr_data['Low']
        self.atr_data['ATR'] = self.atr_data['RNG'].rolling(window=20).mean()
        atr = self.atr_data['ATR']
        atr.dropna(inplace=True)
        return atr
    
    def cc(self):
        self.data = self.data
        if self.underlying == '^GSPC':
            self.vol = yf.Ticker('^VIX')
        elif self.underlying == '^NDX':
            self.vol = yf.Ticker('^VXN')
        vix = self.vol.history(interval='1d', start=self.start_date,
                                 end=self.end_date)
        vix.index = vix.index.date
        close_close = pd.DataFrame(self.data['Close'])
        close_close['Return'] = np.log(close_close['Close'] /
                                       close_close['Close'].shift(1))
        close_close.dropna(inplace=True)
        close_close['std'] = close_close['Return'].rolling(window=30).std()
        close_close['Vol'] = close_close['std'] * np.sqrt(252)
        close_close['VRP'] = vix['Close'] - (close_close['Vol'] * 100)
        rvol = close_close['VRP']
        rvol.dropna(inplace=True)
        return rvol

def plot_signals(df):
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['Price'], label='S&P 500')
    plt.fill_between(df.index, df['Price'], color='r', where=(df['State']==1), alpha=0.3)
    plt.fill_between(df.index, df['Price'], color='g', where=(df['State']==0), alpha=0.3)
    plt.title('Gaussian Hidden Markov Model')
    plt.legend();

def plot_performance(data):
    starting_balance = 10000
    data['Position'] = np.where(data['State'] == 1, 0, 1)
    data['Cumret'] = ((1 + data['Returns']).cumprod() - 1)
    data['Strategy'] = ((1 + data['Returns'] * data['Position']).cumprod() - 1)
    data['ReturnsD'] = starting_balance * (1 + data['Returns']).cumprod()
    data['StrategyD'] = starting_balance * (1 + data['Strategy'])
    fig, ax1 = plt.subplots(2, 1, figsize=(10, 8))
    plt.subplot(211)
    plt.plot(data.index, data['Price'], label='S&P 500')
    plt.fill_between(data.index, data['Price'], color='r', where=(data['State']==1), alpha=0.3)
    plt.fill_between(data.index, data['Price'], color='g', where=(data['State']==0), alpha=0.3)
    plt.legend()
    plt.title('Gaussian Hidden Markov Model')
    plt.subplot(212)
    plt.plot(data['Strategy'], label='HMM Strategy', color='m')
    plt.plot(data['Cumret'], label='Long')
    plt.ylabel('Returns')
    plt.title('Strategy Returns vs. Underlying')
    plt.legend()
    plt.show();
