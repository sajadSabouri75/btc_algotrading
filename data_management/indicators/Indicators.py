import math
import numpy as np
from finta import TA
import pandas as pd


class Indicators:
    def __init__(self, df):
        self.df = df

    def accumulation_distribution(self):
        self.df['accumulation_distribution'] = (2 * self.df.close - self.df.high - self.df.low) \
                                               * self.df.volume / (self.df.high - self.df.low)

    def SMACollection(self, listOfPeriods):
        for period in listOfPeriods:
            self.df['sma_' + str(period)] = self.SMA(self.df.close, period)

    def bollinger_bands(self, period):
        mean = self.df.close.rolling(period).mean()
        stddev = self.df.close.rolling(period).std()
        self.df['boll_hi'] = mean + 2.5 * stddev
        self.df['boll_mid'] = self.SMA(self.df.close, 20)
        self.df['boll_lo'] = mean - 2.5 * stddev
        return self.df['boll_lo'], self.df['boll_mid'], self.df['boll_hi']

    def ema(self, period):
        return self.df.close.ewm(span=period).mean()

    def emaCollection(self, listOfPeriods):
        for period in listOfPeriods:
            self.df['ema_' + str(period)] = self.ema(period)

    def heikin_ashi(self):
        self.df['h_close'] = (self.df.open + self.df.close + self.df.high + self.df.low) * 0.25
        self.df['h_open'] = (self.df.open.shift() + self.df.close.shift()) * 0.5
        self.df['h_high'] = self.df[['high', 'h_open', 'h_close']].max(axis=1)
        self.df['h_low'] = self.df[['low', 'h_open', 'h_close']].min(axis=1)

    def on_balance_volume(self):
        obv = self.df.volume.copy()
        obv[self.df.close < self.df.close.shift()] = -obv
        obv[self.df.close == self.df.close.shift()] = 0
        self.df['obv'] = obv.cumsum()

    def rsi(self, period, name='rsi'):
        diff = self.df.close.diff().values
        gains = diff
        losses = -diff
        with np.errstate(invalid='ignore'):
            gains[(gains < 0) | np.isnan(gains)] = 0.0
            losses[(losses <= 0) | np.isnan(losses)] = 1e-10  # we don't want divide by zero/NaN
        n = period
        m = (n - 1) / n
        ni = 1 / n
        g = gains[n] = np.nanmean(gains[:n])
        l = losses[n] = np.nanmean(losses[:n])
        gains[:n] = losses[:n] = np.nan
        for i, v in enumerate(gains[n:], n):
            g = gains[i] = ni * v + m * g
        for i, v in enumerate(losses[n:], n):
            l = losses[i] = ni * v + m * l
        rs = gains / losses
        self.df[name] = 100 - (100 / (1 + rs))
        return self.df[name]

    def vma(self):
        self.df['vma'] = self.df.volume.rolling(20).mean()

    def macd(self):
        self.df['macd'] = self.ema(12) - self.ema(26)
        self.df['macds'] = self.df.macd.ewm(span=9).mean()
        self.df['macdh'] = self.df['macd'] - self.df['macds']
        return self.df['macdh']

    def movingAverage(self, period):
        self.df['moving_average'] = self.df.close.rolling(period).mean()

    def ichimuku_lines(self):
        self.df['tenkan_sen'] = (self.df['high'].rolling(window=9).max() + self.df['low'].rolling(window=9).min()) / 2.0
        self.df['kijun_sen'] = (self.df['high'].rolling(window=26).max() + self.df['low'].rolling(
            window=26).min()) / 2.0
        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
        self.df['senkou_span_a'] = ((self.df['tenkan_sen'] + self.df['kijun_sen']) / 2).shift(26)
        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        self.df['senkou_span_b'] = (
                    (self.df['high'].rolling(window=52).max() + self.df['low'].rolling(window=52).min()) / 2).shift(26)
        # The most current closing price plotted 22 time periods behind (optional)
        self.df['chikou_span'] = self.df['close'].shift(-22)  # 22 according to investopedia

    def cci(self, period):
        """
        CCI (Commodity Chanel Index) for n bars close price.​
        CCI = (Typical Price − MA) / 0.015 * Mean Deviation
        where:
            Typical Price = ∑P((H + L + C) / 3))
            P = number of bars (period)
            MA = Moving Average = (∑P Typical Price) / P
            Mean Deviation=(∑P | Typical Price - MA |) / P
        """
        TP = (self.df['high'] + self.df['low'] + self.df['close']) / 3.0
        self.df['cci'] = (TP - TP.rolling(period).mean()) / (0.015 * TP.rolling(period).std())
        return self.df['cci']

    def adx(self, period):
        """
        Computes the ADX indicator.
        First ADX14 = 14 period Average of DX
        Second ADX14 = ((First ADX14 x 13) + Current DX Value)/14
        Subsequent ADX14 = ((Prior ADX14 x 13) + Current DX Value)/14
        """
        alpha = 1 / period

        # TR
        self.df['H-L'] = self.df['high'] - self.df['low']
        self.df['H-C'] = np.abs(self.df['high'] - self.df['close'].shift(1))
        self.df['L-C'] = np.abs(self.df['low'] - self.df['close'].shift(1))
        TR = self.df[['H-L', 'H-C', 'L-C']].max(axis=1)
        del self.df['H-L'], self.df['H-C'], self.df['L-C']

        # ATR
        ATR = TR.ewm(alpha=alpha, adjust=False).mean()

        # +-DX
        self.df['H-pH'] = self.df['high'] - self.df['high'].shift(1)
        self.df['pL-L'] = self.df['low'].shift(1) - self.df['low']
        self.df['+DX'] = np.where((self.df['H-pH'] > self.df['pL-L']) & (self.df['H-pH'] > 0), self.df['H-pH'], 0.0)
        self.df['-DX'] = np.where((self.df['H-pH'] < self.df['pL-L']) & (self.df['pL-L'] > 0), self.df['pL-L'], 0.0)
        del self.df['H-pH'], self.df['pL-L']

        # +- DMI
        S_plus_DM = self.df['+DX'].ewm(alpha=alpha, adjust=False).mean()
        S_minus_DM = self.df['-DX'].ewm(alpha=alpha, adjust=False).mean()
        del self.df['+DX'], self.df['-DX']
        DMI_plus = (S_plus_DM / ATR) * 100
        DMI_minus = (S_minus_DM / ATR) * 100

        # ADX
        DX = (np.abs(DMI_plus - DMI_minus) / (DMI_plus + DMI_minus)) * 100
        self.df['adx'] = DX.ewm(alpha=alpha, adjust=False).mean()

    def stoch(self, close, high, low, period: int = 14):
        """Stochastic oscillator %K
            The stochastic oscillator is a momentum indicator comparing the closing price of a security
            to the period of its prices over a certain period of time.
            The sensitivity of the oscillator to market movements is reducible by adjusting that time
            period or by taking a moving average of the result.
        """

        highest_high = high.rolling(center=False, window=period).max()
        lowest_low = low.rolling(center=False, window=period).min()

        STOCH = pd.Series(
            (close - lowest_low) / (highest_high - lowest_low) * 100,
            name="{0} period STOCH %K".format(period),
        )

        return STOCH

    def SMA(self, close, period: int = 41):
        """
        Simple moving average - rolling mean in pandas lingo. Also known as 'MA'.
        The simple moving average (SMA) is the most basic of the moving averages used for trading.
        """
        return pd.Series(
            close.rolling(window=period).mean(),
            name="{0} period SMA".format(period))

    def coppock_curve(self):
        self.df['coppock_curve'] = TA.COPP(self.df)

    def chaikin(self):
        self.df['chaikin'] = TA.CHAIKIN(self.df)

    def mfi(self, period):
        self.df['mfi'] = TA.MFI(self.df, period=period)

    def ultimate_oscillator(self):
        self.df['uo'] = TA.UO(self.df)

    def dt_oscillator(self, period1, period2, period3):
        source = self.df['close']
        lengthRSI = period3
        lengthStoch = period2
        smoothK = period1
        smoothD = period1
        rsi1 = TA.RSI(self.df, column='close', period=lengthRSI)
        stochRSI = self.stoch(rsi1, rsi1, rsi1, period=lengthStoch)
        k = self.SMA(stochRSI, period=smoothK)
        d = self.SMA(k, period=smoothD)
        self.df['dt-k'], self.df['dt-d'] = k, d
        self.df['dt'] = k
        return k, d

    def awesome_oscillator(self):
        median = (self.df.high + self.df.low) / 2
        sma5 = self.SMA(median, 5)
        sma34 = self.SMA(median, 34)
        ao = sma5 - sma34
        self.df['ao'] = ao
        return ao

    def closeIndicator(self):
        return self.df.close

    def WilliamsAlligator(self, jaw: int = 13, teeth: int = 8, lips: int = 5):

        mean = (self.df['high'] + self.df['low']) / 2.0
        jaw_oc = self.SMA(mean, jaw)
        teeth_oc = self.SMA(mean, teeth)
        lips_oc = self.SMA(mean, lips)
        self.df['jaw'], self.df['teeth'], self.df['lips'] = jaw_oc, teeth_oc, lips_oc
        return jaw_oc, teeth_oc, lips_oc

    def WilliamR(self, period=14):
        max = self.df.close.rolling(window=period).max()
        min = self.df.close.rolling(window=period).min()
        self.df['WilliamR'] = 100 * (self.df.close - max) / (max - min)
        return self.df.WilliamR

    def getDataSource(self):
        return self.df

    def atr(self, period=14):
        atr = (self.df.high - self.df.close).rolling(window=period).mean()
        self.df['atr'] = atr
        return atr

    def momentum(self, period=10):
        momentum = self.df.close.diff(period)
        self.df['momentum'] = self.SMA(momentum, 5)
        return self.df['momentum']

    def williams_fractal(self, period=5):
        periods = range(-period, period + 1)
        high_fractals_times = pd.Series(np.logical_and.reduce(
            [
                self.df.high >= self.df.high.shift(period) for period in periods
            ]), index=self.df.index
        )
        low_fractals_times = pd.Series(np.logical_and.reduce(
            [
                self.df.low <= self.df.low.shift(period) for period in periods
            ]), index=self.df.index
        )
        self.df['low_fractals'], self.df['high_fractals'] = low_fractals_times, high_fractals_times
        return low_fractals_times, high_fractals_times
