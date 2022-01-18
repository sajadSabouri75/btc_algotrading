import time
from data_management.data_center_builders import csv_datacenter_builder as data_builder


def main():

    # > helpful directories
    inputs_relative_addresses, outputs_partial_relative_address = \
        generate_helpful_directories('datasources', '/', ['btc_1h_01', 'btc_15m_01'], 'csv')

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


    # calling it off
    print('hi')


def generate_helpful_directories(inputs_root_directory, directory_separator, datasource_files_names,
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
        'rsi_14',
        'cci',
        'atr',
        'macd'
    ]
    return dependent_series_names


if __name__ == '__main__':
    startTime = time.time()
    main()
    endTime = time.time()
    print('Total time passed: ' + str(round(endTime - startTime)) + ' seconds.')
