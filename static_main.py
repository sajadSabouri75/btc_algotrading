import math
import time
from data_management.data_center_builders import csv_datacenter_builder as data_builder
from trading.traders import CommandTrader as td
from trading.traders import IntelligentTrader as it, CommandTrader as td
from trading.Investors import Investor as inv
from simulation import static_bot_simulation as simulator_lib
from matplotlib import pyplot as plt
import numpy as np
import matplotlib.colors as mcolors


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
    target_series_max_index = math.inf
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
        fractal_period=2
    )
    datasource = simulator.simulate()
    datacenter_builder.setDatasource(datasource)
    datacenter_builder.saveDataCenter('final_datacenter')

    # define a command trader -> a broker which places orders and manages transaction process
    commandTrader = td.CommandTrader(id='1', name='myTrader', dataCenter=datacenters[0])

    # define an intelligent trader -> a trader which orders command trader to places orders
    intelligentTrader = it.IntelligentTrader(
        dataCenter=datacenters[0],
        trader=commandTrader,
        requiredWeakSignalsToEnter=0,
        requiredWeakSignalsCountToExit=0,
        requiredWeakSignalsCountToEnterTest=0,
        requiredWeakSignalsCountToExitTest=0,
        hasStoplossTraining=False,
        hasStoplossTest=False)

    # set intelligent trader to command trader
    commandTrader.setSubject(intelligentTrader)

    # define an investor -> the investor knows the naive trader it is working with
    investor = inv.Investor(
        capital=100000, investmentPerTrade=1000, trader=intelligentTrader,
        trainingMinNumberOfTrades=30, testMinNumberOfTrades=5,
        trainingMaxNumberOfTrades=100, testMaxNumberOfTrades=70,
        trainingSimilarityThreshold=1, testSimilarityThreshold=1,
        trainingMinWinRate=0.75, testMinWinRate=0.65
    )

    # set investor to intelligent trader -> naive trader must know the investor as well
    intelligentTrader.setInvestor(investor)

    # simulate investment
    investor.invest()

    # plot trading points
    intelligentTrader.reportResults()
    drawCloseSeriesPlot(investor, datacenters[0])
    benefitSeries, trainingPercent = investor.updateBenefitSeries()
    investor.plotBenefitSeries(1, 2, benefitSeries, trainingPercent)


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
        'dt',
        'obv'
    ]
    return dependent_series_names


def drawCloseSeriesPlot(investor, dataCenter, outputDirectory=None, savePlot=True, dpi=600,
                        titleCounter=1):
    Xs = range(0, len(dataCenter.getDatasource()))
    closeSeries = dataCenter.getSeriesOf(['close'])

    buyPointsStart = []
    sellPointsStart = []
    buyPointsEnd = []
    sellPointsEnd = []

    colorsStopBuy = []
    colorsStartBuy = []
    colorsStartSell = []
    colorsStopSell = []

    if investor is not None:

        for order in investor.getOrders():
            if order.getTradingType() == 'buy':
                colorsStartBuy.append(mcolors.TABLEAU_COLORS['tab:blue'])
                buyPointsStart.append(order.getStartTimeIndex())
                buyPointsEnd.append(order.getEndTimeIndex())
                if order.getDidStoplossReach():
                    colorsStopBuy.append(mcolors.CSS4_COLORS['dimgray'])
                else:
                    colorsStopBuy.append(mcolors.TABLEAU_COLORS['tab:cyan'])

            elif order.getTradingType() == 'sell':
                colorsStartSell.append(mcolors.CSS4_COLORS['red'])
                sellPointsStart.append(order.getStartTimeIndex())
                sellPointsEnd.append(order.getEndTimeIndex())
                if order.getDidStoplossReach():
                    colorsStopSell.append(mcolors.CSS4_COLORS['dimgray'])
                else:
                    colorsStopSell.append(mcolors.CSS4_COLORS['tomato'])

    updateTradingPlot(
        Xs, closeSeries, 1, 1, 'transactions',
        buyPointsStart, sellPointsStart, buyPointsEnd, sellPointsEnd,
        colorsStartBuy, colorsStopBuy, colorsStartSell, colorsStopSell)

    # plt.tight_layout()
    # if savePlot:
    #     plt.savefig(outputDirectory + '/' + 'transactions_' + str(titleCounter) + '.png', bbox_inches='tight', dpi=dpi)


def updateTradingPlot(xPoints, yPoints, figureIndex, subPlotPosition, title='unknown title',
                      buyPoints=None, sellPoints=None, stopBuyPoints=None, stopSellPoints=None,
                      colorsStartBuy=None, colorsStopBuy=None, colorsStartSell=None, colorsStopSell=None):
    plt.figure(figureIndex)
    plt.subplot(2, 1, subPlotPosition)
    # plt.subplots(sharex=True)
    plt.title(title)
    plt.plot(xPoints, yPoints, 'c-', linewidth=0.5)
    if buyPoints is not None:
        if len(buyPoints) != 0:
            for i in range(0, len(buyPoints)):
                plt.scatter(buyPoints[i], yPoints.iloc[buyPoints[i]], s=35, facecolors='none',
                            edgecolors=colorsStartBuy[i], linewidths=2, marker='^')
    if sellPoints is not None:
        if len(sellPoints) != 0:
            for i in range(0, len(sellPoints)):
                plt.scatter(sellPoints[i], yPoints.iloc[sellPoints[i]], s=35, facecolors='none',
                            edgecolors=colorsStartSell[i], linewidths=2, marker='v')
    if stopBuyPoints is not None:
        if len(stopBuyPoints) != 0:
            for i in range(0, len(stopBuyPoints)):
                plt.scatter(stopBuyPoints[i], yPoints.iloc[stopBuyPoints[i]], s=30, facecolors=colorsStopBuy[i],
                            edgecolors='none', marker='v')
    if stopSellPoints is not None:
        if len(stopSellPoints) != 0:
            for i in range(0, len(stopSellPoints)):
                plt.scatter(stopSellPoints[i], yPoints.iloc[stopSellPoints[i]], s=30, facecolors=colorsStopSell[i],
                            edgecolors='none', marker='^')
    plt.draw()
    plt.pause(0.5)


if __name__ == '__main__':
    startTime = time.time()
    main()
    endTime = time.time()
    print('Total time passed: ' + str(round(endTime - startTime)) + ' seconds.')
