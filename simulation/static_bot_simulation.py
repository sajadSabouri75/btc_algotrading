import numpy as np
import pandas as pd


class StaticBotSimulator:
    def __init__(self, **kwargs):
        self._target_datacenter = kwargs['target_datacenter'] if 'target_datacenter' else None
        self._dependent_datacenters = kwargs['dependent_datacenters'] if 'dependent_datacenters' in kwargs else None
        self._n_candles = self._target_datacenter.getDatasource().shape[0]
        self._current_target_index = 0
        self._fractal_period = kwargs['fractal_period'] if 'fractal_period' in kwargs else 2
        self._secondary_fractal_period = kwargs[
            'secondary_fractal_period'] if 'secondary_fractal_period' in kwargs else 2
        self._high_fractals_indices = \
            np.array(
                [i for i in range(self._n_candles) if self._target_datacenter.getSeriesOf('high_fractals')[i]]
            )
        self._low_fractals_times = \
            np.array(
                [i for i in range(self._n_candles) if self._target_datacenter.getSeriesOf('low_fractals')[i]])
        self._secondary_high_fractals_indices = \
            np.array(
                [i for i in range(self._n_candles) if self._target_datacenter.getSeriesOf('secondary_high_fractals')[i]]
            )
        self._secondary_low_fractals_times = \
            np.array(
                [i for i in range(self._n_candles) if self._target_datacenter.getSeriesOf('secondary_low_fractals')[i]])

        self._n_true_divergences_main = 1
        self._n_true_divergences_secondary = 1

    def simulate(self):
        all_indicators = ['high', 'low', 'cci', 'rsi', 'obv', 'momentum']
        main_indicators = ['cci']
        secondary_indicators = ['rsi']
        series = self._target_datacenter.getSeriesOf(all_indicators)
        self._target_datacenter.getDatasource()['buy signals'] = False
        self._target_datacenter.getDatasource()['sell signals'] = False

        for current_index in range(self._n_candles):
            self._target_datacenter.getDatasource().loc[current_index, 'sell signals'] = \
                self.check_sell_signal(current_index, series, main_indicators, secondary_indicators)
            self._target_datacenter.getDatasource().loc[current_index, 'buy signals'] = \
                self.check_buy_signal(current_index, series, main_indicators, secondary_indicators)

        return self._target_datacenter.getDatasource()

    def check_sell_signal(self, current_index, series, main_indicators, secondary_indicators):
        accessible_high_fractals = self.get_last_accessible_fractals(
            self._high_fractals_indices,
            self._secondary_high_fractals_indices,
            self._low_fractals_times,
            current_index
        )
        if len(accessible_high_fractals) == 3:
            if series['high'].iloc[current_index] < series['high'].iloc[accessible_high_fractals[2]]:
                values_for_divergence_check = series.iloc[accessible_high_fractals]
                if values_for_divergence_check['high'].iloc[2] < values_for_divergence_check['high'].iloc[1] > \
                        values_for_divergence_check['high'].iloc[0]:
                    diff_high = values_for_divergence_check['high'].iloc[1] - values_for_divergence_check['high'].iloc[
                        0]
                    # main divergences
                    diffs_main = [
                        values_for_divergence_check[target_indicator].iloc[1] -
                        values_for_divergence_check[target_indicator].iloc[0]
                        for target_indicator in main_indicators
                    ]
                    diffs = [diff_high * diff for diff in diffs_main]
                    diffs_array = np.array(diffs)
                    diffs_bool_array = diffs_array < 0
                    diffs_bool_true_main = diffs_bool_array[diffs_bool_array]
                    # secondary divergences
                    diffs_secondary = [
                        values_for_divergence_check[target_indicator].iloc[1] -
                        values_for_divergence_check[target_indicator].iloc[0]
                        for target_indicator in secondary_indicators
                    ]
                    diffs = [diff_high * diff for diff in diffs_secondary]
                    diffs_array = np.array(diffs)
                    diffs_bool_array = diffs_array < 0
                    diffs_bool_true_secondary = diffs_bool_array[diffs_bool_array]

                    if len(diffs_bool_true_main) >= self._n_true_divergences_main and len(
                            diffs_bool_true_secondary) >= self._n_true_divergences_secondary:
                        return True

        return False

    def check_buy_signal(self, current_index, series, main_indicators, secondary_indicators):
        accessible_low_fractals = self.get_last_accessible_fractals(
            self._low_fractals_times,
            self._secondary_low_fractals_times,
            self._high_fractals_indices,
            current_index
        )
        if len(accessible_low_fractals) == 3:
            if series['low'].iloc[current_index] > series['low'].iloc[accessible_low_fractals[2]]:
                values_for_divergence_check = series.iloc[accessible_low_fractals]
                if values_for_divergence_check['low'].iloc[2] > values_for_divergence_check['low'].iloc[1] < \
                        values_for_divergence_check['low'].iloc[0]:
                    diff_low = values_for_divergence_check['low'].iloc[1] - values_for_divergence_check['low'].iloc[0]
                    # main divergences
                    diffs_main = [
                        values_for_divergence_check[target_indicator].iloc[1] -
                        values_for_divergence_check[target_indicator].iloc[0]
                        for target_indicator in main_indicators
                    ]
                    diffs = [diff_low * diff for diff in diffs_main]
                    diffs_array = np.array(diffs)
                    diffs_bool_array = diffs_array < 0
                    diffs_bool_true_main = diffs_bool_array[diffs_bool_array]
                    # secondary divergences
                    diffs_secondary = [
                        values_for_divergence_check[target_indicator].iloc[1] -
                        values_for_divergence_check[target_indicator].iloc[0]
                        for target_indicator in secondary_indicators
                    ]
                    diffs = [diff_low * diff for diff in diffs_secondary]
                    diffs_array = np.array(diffs)
                    diffs_bool_array = diffs_array < 0
                    diffs_bool_true_secondary = diffs_bool_array[diffs_bool_array]

                    if len(diffs_bool_true_main) >= self._n_true_divergences_main and len(
                            diffs_bool_true_secondary) >= self._n_true_divergences_secondary:
                        return True
        return False

    def get_last_accessible_fractals(self, fractals, secondary_fractals, counterpart_fractals, current_index):
        if self._fractal_period == self._secondary_fractal_period:
            selected_fractals_indices = 3
        else:
            selected_fractals_indices = 2

        selected_fractals = \
            fractals[
                fractals < current_index - self._fractal_period
                ][-selected_fractals_indices:]

        counterpart_selected_fractals = \
            counterpart_fractals[
                counterpart_fractals < current_index - self._fractal_period
                ][-1:]

        selected_secondary_fractals = \
            secondary_fractals[
                secondary_fractals < current_index - self._secondary_fractal_period
                ][-1:]

        if ((len(selected_fractals) == 2 and selected_secondary_fractals == 2) or (len(selected_fractals) == 3)) and \
                len(selected_secondary_fractals) == 1 and \
                len(counterpart_selected_fractals) == 1:
            if selected_secondary_fractals[0] > selected_fractals[1] or selected_fractals_indices == 3:
                if selected_fractals[1] > counterpart_selected_fractals[0]:
                    if selected_fractals_indices == 3:
                        return selected_fractals
                    else:
                        selected_fractals = np.append(selected_fractals, selected_secondary_fractals[0])
                        return selected_fractals
        return []
