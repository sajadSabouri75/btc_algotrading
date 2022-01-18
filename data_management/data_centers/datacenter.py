import pandas as pd
import math
import numpy as np


class DataCenter:
    def __init__(self, **kwargs):
        self._dataSource = kwargs['dataSource'] if 'dataSource' in kwargs else None
        self._dataSource.reset_index(drop=True, inplace=True)
        self._currentSource = self._dataSource

    def getMaxIndex(self):
        return self._currentSource.shape[0] - 1

    def getClosePrice(self, index):
        if index >= 0:
            requestedRow = self._currentSource.iloc[index]
            out = requestedRow['close']
            if math.isnan(out):
                return None
            else:
                return out
        else:
            return None

    def getMinValueOfSeriesOf(self, seriesName):
        series = [x for x in self._currentSource[seriesName] if not np.isnan(x)]
        return min(series)

    def getMaxValueOfSeriesOf(self, seriesName):
        series = [x for x in self._currentSource[seriesName] if not np.isnan(x)]
        return max(series)

    def getDatasource(self):
        return self._dataSource

    def getCurrentSource(self):
        return self._currentSource

    def getCloseSeries(self):
        return self._currentSource['close']

    def getSeriesOf(self, seriesName):
        return self._currentSource[seriesName]

    def getMaxNanValueThreshold(self):
        maxNumOfNan = 0
        for i in range(self._currentSource.shape[1]):
            selectedColumn = self._currentSource.iloc[:, i]
            selectedColumnOfNan = [x for x in selectedColumn if str(x) == 'nan']
            if len(selectedColumnOfNan) > maxNumOfNan:
                maxNumOfNan = len(selectedColumnOfNan)
        return maxNumOfNan + 1

    def getMaxNanValueThresholdOf(self, seriesName):
        selectedColumn = self._currentSource.loc[:, seriesName]
        selectedColumnOfNan = [x for x in selectedColumn if str(x) == 'nan']

        return len(selectedColumnOfNan)
