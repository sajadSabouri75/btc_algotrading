from data_management.data_center_builders import datacenter_builder as data_builder
import pandas as pd


class CSVDataCenterBuilder(data_builder.DataCenterBuilder):
    def __init__(self, **kwargs):
        super(CSVDataCenterBuilder, self).__init__(**kwargs)
        self.inputs_files_address = kwargs['fileName'] if 'fileName' in kwargs else None
        self._datacenters = []

    def buildDataCenter(self):
        datasources = [
            pd.read_csv(input_file_name) for input_file_name in self.inputs_files_address
        ]

        datasource_counter = 0
        for datasource in datasources:
            datasource_counter += 1
            self._dataSource = datasource
            self._datacenters.append(
                super(CSVDataCenterBuilder, self).buildDataCenter(
                    'datacenter_' + str(datasource_counter)
                )
            )

        return self._datacenters
