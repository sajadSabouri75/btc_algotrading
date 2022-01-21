import time
from data_management.data_center_builders import csv_datacenter_builder as data_builder
from simulation import static_bot_simulation as simulator_lib
from matplotlib import pyplot as plt
import numpy as np


def main():
    # > helpful directories
    inputs_relative_addresses, outputs_partial_relative_address = \
        generate_helpful_directories('datasources', '/', ['btc_30m', 'btc_5m'], 'csv')

    # > data import and build
    # dependent series to work with
    dependent_series_names = get_dependent_series_names()

    # define a data center builder to manage import and generation of series
    target_series_columns = ['time', 'close', 'high', 'low', 'open', 'volume', 'amount', 'index']
    target_series_min_index = 0
    target_series_max_index = 10000
    datacenter_builder = data_builder.CSVDataCenterBuilder(
        fileName=inputs_relative_addresses,
        minDataBound=target_series_min_index,
        maxDataBound=target_series_max_index,
        targetColumns=target_series_columns,
        targetIndicators=dependent_series_names,
        outputDirectory=outputs_partial_relative_address
    )
    datacenters = datacenter_builder.buildDataCenter()

    # simulation
    simulator = simulator_lib.StaticBotSimulator(
        target_datacenter=datacenters[0],
        dependent_datacenters=datacenters[1:],
        fractal_period=5
    )
    datasource = simulator.simulate()
    datacenter_builder.setDataCenter(datasource)
    datacenter_builder.saveDataCenter('final_datacenter')

    # plot signal points
    plt.figure(0)
    buy_signals = np.array(datasource['buy signals'])
    sell_signals = np.array(datasource['sell signals'])
    high_series = np.array(datasource['high'])
    indices = np.array(datasource.index)
    buy_indices = indices[buy_signals == True]
    sell_indices = indices[sell_signals == True]
    y_high_buy = high_series[buy_indices]
    y_high_sell = high_series[sell_indices]
    plt.plot(high_series, linewidth=1)
    plt.scatter(buy_indices, y_high_buy, s=15, c='g')
    plt.scatter(sell_indices, y_high_sell, s=15, c='r')
    plt.show()

    # calling it off
    print('hi')


def generate_helpful_directories(
        inputs_root_directory,
        directory_separator,
        datasource_files_names,
        datasource_files_format):
    directory_separator = '/'
    # inputs
    inputs_relative_addresses = [
        inputs_root_directory + directory_separator + file_name + '.' + datasource_files_format for file_name in
        datasource_files_names
    ]
    # outputs
    outputs_root_directory = 'outputs'
    outputs_partial_relative_address = outputs_root_directory + directory_separator

    return inputs_relative_addresses, outputs_partial_relative_address


def get_dependent_series_names():
    dependent_series_names = [
        'rsi',
        'cci',
        'macd',
        'williams_fractal',
        'dt'
    ]
    return dependent_series_names


if __name__ == '__main__':
    startTime = time.time()
    main()
    endTime = time.time()
    print('Total time passed: ' + str(round(endTime - startTime)) + ' seconds.')
