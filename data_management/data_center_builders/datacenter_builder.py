from data_management.data_centers import datacenter
from data_management.indicators import Indicators
import os


class DataCenterBuilder:
    def __init__(self, **kwargs):
        self._dataCenter = None
        self._dataSource = None
        self._targetColumns = kwargs['targetColumns'] if 'targetColumns' in kwargs else None
        self._minDataBound = kwargs['minDataBound'] if 'minDataBound' in kwargs else 0
        self._maxDataBound = kwargs['maxDataBound'] if 'maxDataBound' in kwargs else 0
        self._targetIndicators = kwargs['targetIndicators'] if 'targetIndicators' in kwargs else None
        self._outputDirectory = kwargs['outputDirectory'] if 'outputDirectory' in kwargs else ''

    def setDataCenter(self, dataSource):
        self._dataSource = dataSource

    def buildDataCenter(self, outputName):
        dataSource = self._dataSource

        dataSource = dataSource[dataSource.index < self._maxDataBound]
        dataSource = dataSource[dataSource.index >= self._minDataBound]

        dataSource.reset_index(drop=True, inplace=True)

        dataSource = dataSource.filter(self._targetColumns)

        self._dataSource = dataSource

        self.addIndicatorsToDataSource()

        self._dataCenter = datacenter.DataCenter(
            dataSource=self._dataSource,
        )

        self.saveDataCenter(outputName)

        return self._dataCenter

    def addIndicatorsToDataSource(self):
        indicatorGenerator = Indicators.Indicators(self._dataSource)

        if 'rsi' in self._targetIndicators:
            indicatorGenerator.rsi(14)
        if 'adx' in self._targetIndicators:
            indicatorGenerator.adx(14)
        if 'cci' in self._targetIndicators:
            indicatorGenerator.cci(5)
        if 'mfi' in self._targetIndicators:
            indicatorGenerator.mfi(14)
        if 'dt' in self._targetIndicators:
            indicatorGenerator.dt_oscillator(2, 2, 5)
        if 'macd' in self._targetIndicators:
            indicatorGenerator.macd()
        if 'sma' in self._targetIndicators:
            indicatorGenerator.SMA(self._dataCenter.getCloseSeries())
        if 'chaikin' in self._targetIndicators:
            indicatorGenerator.chaikin()
        if 'vma' in self._targetIndicators:
            indicatorGenerator.vma()
        if 'uo' in self._targetIndicators:
            indicatorGenerator.ultimate_oscillator()
        if 'ao' in self._targetIndicators:
            indicatorGenerator.awesome_oscillator()
        if 'macd' in self._targetIndicators:
            indicatorGenerator.macd()
        if 'alligator' in self._targetIndicators:
            indicatorGenerator.WilliamsAlligator()
        if 'atr' in self._targetIndicators:
            indicatorGenerator.atr()
        if 'bollinger' in self._targetIndicators:
            indicatorGenerator.bollinger_bands(20)
        if 'sma_collection_01' in self._targetIndicators:
            indicatorGenerator.SMACollection([5, 20, 50])
        if 'rsi_11' in self._targetIndicators:
            indicatorGenerator.rsi(11, 'rsi_11')
        if 'ema_collection_01' in self._targetIndicators:
            indicatorGenerator.emaCollection([10, 21, 50])
        if 'momentum_10' in self._targetIndicators:
            indicatorGenerator.momentum(10)
        if 'rsi_2' in self._targetIndicators:
            indicatorGenerator.rsi(2, 'rsi_2')
        if 'williams_fractal' in self._targetIndicators:
            indicatorGenerator.williams_fractal()

    def saveDataCenter(self, outputName):
        if not os.path.exists(self._outputDirectory):
            os.makedirs(self._outputDirectory)
        self._dataSource.to_csv(self._outputDirectory + outputName + '.csv')
