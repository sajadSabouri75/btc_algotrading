import numpy as np
import pandas as pd


class StaticBotSimulator:
    def __init__(self, **kwargs):
        self._target_datacenter = kwargs['target_datacenter'] if 'target_datacenter' else None
        self._dependent_datacenters = kwargs['dependent_datacenters'] if 'dependent_datacenters' in kwargs else None
        self._n_candles = self._target_datacenter.getDatasource().shape[0]
        self._current_target_index = 0
        self._fractal_period = kwargs['fractal_period'] if 'fractal_period' in kwargs else 2
        self._high_fractals_indices = \
            np.array(
                [i for i in range(self._n_candles) if self._target_datacenter.getSeriesOf('high_fractals')[i] == True])
        self._low_fractals_times = \
            np.array(
                [i for i in range(self._n_candles) if self._target_datacenter.getSeriesOf('low_fractals')[i] == True])

    def simulate(self):
        series = self._target_datacenter.getSeriesOf(['high', 'low', 'macdh'])
        self._target_datacenter.getDatasource()['buy signals'] = False
        self._target_datacenter.getDatasource()['sell signals'] = False

        for current_index in range(self._n_candles):
            self._target_datacenter.getDatasource().loc[current_index, 'sell signals'] = self.check_sell_signal(current_index, series)
            self._target_datacenter.getDatasource().loc[current_index, 'buy signals'] = self.check_buy_signal(current_index, series)

        return self._target_datacenter.getDatasource()

    def check_sell_signal(self, current_index, series):
        accessible_high_fractals = self.get_last_accessible_fractals(self._high_fractals_indices, current_index)
        if len(accessible_high_fractals) == 2:
            values_for_divergence_check = series.iloc[accessible_high_fractals]

            diff_high = values_for_divergence_check['high'].iloc[1] - values_for_divergence_check['high'].iloc[0]
            diff_rsi = values_for_divergence_check['macdh'].iloc[1] - values_for_divergence_check['macdh'].iloc[0]
            if diff_high * diff_rsi < 0:
                if diff_high > 0:
                    return True

        return False

    def check_buy_signal(self, current_index, series):
        accessible_low_fractals = self.get_last_accessible_fractals(self._low_fractals_times, current_index)
        if len(accessible_low_fractals) == 2:
            values_for_divergence_check = series.iloc[accessible_low_fractals]

            diff_low = values_for_divergence_check['low'].iloc[1] - values_for_divergence_check['low'].iloc[0]
            diff_rsi = values_for_divergence_check['macdh'].iloc[1] - values_for_divergence_check['macdh'].iloc[0]
            if diff_low * diff_rsi < 0:
                if diff_low < 0:
                    return True

        return False

    def get_last_accessible_fractals(self, fractals, current_index):
        return fractals[fractals < current_index - self._fractal_period][-2:]
