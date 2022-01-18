import time

# time
startSimulationTime = time.time()

# helpful directories
root_directory = 'SampleData'
datasource_file_names = ['btc_1h', 'btc_15m']
datasource_file_format = 'csv'
directory_separator = '/'
input_file_relative_address_es = [
    root_directory + directory_separator + file_name + datasource_file_format for file_name in datasource_file_names
]

minDataBound = 0
maxDataBound = 10000
