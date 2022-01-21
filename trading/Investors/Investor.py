from matplotlib import pyplot as plt
import numpy as np
import math


class Investor:
    def __init__(self, **kwargs):

        # trading settings
        self._capital = kwargs['capital'] if 'capital' in kwargs else 0
        self._investmentPerTrade = kwargs['investmentPerTrade'] if 'investmentPerTrade' in kwargs else None
        self._trader = kwargs['trader'] if 'trader' in kwargs else None

        # objective function settings
        self._trainingMinNumberOfTrades = kwargs['trainingMinNumberOfTrades'] if 'trainingMinNumberOfTrades' in kwargs else None
        self._trainingMaxNumberOfTrades = kwargs['trainingMaxNumberOfTrades'] if 'trainingMaxNumberOfTrades' in kwargs else None
        self._testMinNumberOfTrades = kwargs['testMinNumberOfTrades'] if 'testMinNumberOfTrades' in kwargs else None
        self._testMaxNumberOfTrades = kwargs['testMaxNumberOfTrades'] if 'testMaxNumberOfTrades' in kwargs else None
        self._trainingSimilarityThreshold = kwargs['trainingSimilarityThreshold'] if 'trainingSimilarityThreshold' in kwargs else None
        self._testSimilarityThreshold = kwargs['testSimilarityThreshold'] if 'testSimilarityThreshold' in kwargs else None
        self._trainingMinWinRate = kwargs['trainingMinWinRate'] if 'trainingMinWinRate' in kwargs else None
        self._testMinWinRate = kwargs['testMinWinRate'] if 'testMinWinRate' in kwargs else None

        self._tradingResults = {}
        self._previousBooleanVector = None
        self._currentBooleanVector = None
        self._similarityToPreviousTree = 0
        self._mode = 'training'

    def invest(self):
        self._tradingHistory = self._trader.trade(self._investmentPerTrade)
        return 0

    def setSimilarityThreshold(self, newThreshold):
        self._trainingSimilarityThreshold = newThreshold

    def setTraderStrategy(self, strategy):
        self._trader.resetTrader()
        self._trader.setStrategy(strategy)

    def setMode(self, mode):
        self._mode = mode
        self._trader.setMode(mode)

    def getSimilarityOfTrees(self):
        return self._similarityToPreviousTree

    def evaluateBooleanVectorsSimilarity(self, boolVec1, boolVec2):
        if (boolVec1 is not None) and (boolVec2 is not None):
            if (boolVec2.shape[0] == boolVec1.shape[0]):
                sumSimilar = np.sum(boolVec1 * boolVec2)
                sumVec1 = np.sum(boolVec1)
                sumVec2 = np.sum(boolVec2)
                if sumVec1 > 0 and sumVec2 > 0:
                    return (sumSimilar / sumVec1) * (sumSimilar / sumVec2)
                if (sumVec1 > 0 and sumVec2 == 0) or (sumVec1 == 0 and sumVec2 > 0):
                    return 0
                else:
                    return 1
        return 0

    def printActivity(self):
        self._trader.reportResults()

    def printOrdersDetails(self):
        self._trader.reportOrdersDetails()

    def getOrders(self):
        return self._trader.getOrders()

    def updateBenefitSeries(self):
        benefitSeries = self._trader.updateBenefitSeries()
        return benefitSeries, self._tradingHistory['benefitPercent']

    @staticmethod
    def plotBenefitSeries(figureIndex, subplotPosition, benefitSeries, trainingBenefitPercent):
        plt.figure(figureIndex)
        ax = plt.subplot(211)
        plt.subplot(2, 1, subplotPosition, sharex=ax)
        xPoints = range(len(benefitSeries))
        yPoints = benefitSeries
        plt.plot(xPoints, yPoints, 'r-')
        plt.title(f'average benefit percent -> training: {trainingBenefitPercent}')
        plt.draw()
        plt.pause(0.1)
        plt.show(block=True)
        plt.grid()
