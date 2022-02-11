from trading.Transactions.CryptoOrder import CryptoOrder
import numpy as np


class IntelligentTrader:
    def __init__(self, **kwargs):
        self._dataCenter = kwargs['dataCenter'] if 'dataCenter' in kwargs else None
        self._trader = kwargs['trader'] if 'trader' in kwargs else None
        self._subject = None
        self._strategyIndex = None
        self._strategyStopBuyIndex = None
        self._buyHistory = np.zeros(self._dataCenter.getMaxIndex() + 1)
        self._sellHistory = np.zeros(self._dataCenter.getMaxIndex() + 1)
        self._startTradeIndex = None

        self._requiredWeakSignalsCountToEnter = \
            kwargs['requiredWeakSignalsToEnter'] if 'requiredWeakSignalsToEnter' else None
        self._requiredWeakSignalsCountToExit = \
            kwargs['requiredWeakSignalsCountToExit'] if 'requiredWeakSignalsCountToExit' else None
        self._requiredWeakSignalsCountToEnterTest = \
            kwargs['requiredWeakSignalsCountToEnterTest'] if 'requiredWeakSignalsCountToEnterTest' else None
        self._requiredWeakSignalsCountToExitTest = \
            kwargs['requiredWeakSignalsCountToExitTest'] if 'requiredWeakSignalsCountToExitTest' else None

        self._hasStoplossTraining = kwargs['hasStoplossTraining'] if 'hasStoplossTraining' else None
        self._hasStoplossTest = kwargs['hasStoplossTest'] if 'hasStoplossTest' else None

        self._state = 'enter'
        self.resetTrader()

    def parseStrategy(self):
        pass

    def setStrategy(self, strategy):
        self._strategy = strategy
        self.parseStrategy()

    def getCurrentTime(self):
        return self._timeIndex

    def setMode(self, mode):
        self._dataCenter.setMode(mode)
        self._mode = mode

    def resetTrader(self):
        self._state = 'enter'
        self._strategy = None
        self._timeIndex = 0
        self._startTimeIndex = 0
        self._endTimeIndex = 0
        self._orders = []
        self._totalBenefit = 0
        self._winRate = None
        self._wons = 0
        self._losts = 0
        self._failures = 0
        self._numberOfOrders = 0
        self._results = {}
        self._numberOfSells = 0
        self._numberOfBuys = 0
        self._totalInvestment = 0
        self._benefitPercent = 0
        self._buyHistory = np.zeros(self._dataCenter.getMaxIndex() + 1)
        self._sellHistory = np.zeros(self._dataCenter.getMaxIndex() + 1)
        self._startTradeIndex = None

    def setInvestor(self, investor):
        self._subject = investor

    def incrementTime(self):
        self._timeIndex += 1

        if self._timeIndex > self._dataCenter.getMaxIndex():
            return False

        return True

    def trade(self):
        totalBenefit = 0
        continueTrading = True
        self._timeIndex = self._startTimeIndex
        self._startTradeIndex = self._timeIndex
        self._buyWeakSignalAchievedCounts = 0
        self._sellWeakSignalAchievedCounts = 0
        self._leverage = 5

        while continueTrading:

            if self.verifyTrigger('buy') and not self.verifyTrigger('sell'):
                self._state = 'exit'
                self._buyWeakSignalAchievedCounts = 0
                self._sellWeakSignalAchievedCounts = 0

                investmentPerTrade = self._subject.get_investment_per_trade()
                self._startTradeIndex = self._timeIndex
                self._buyHistory[self._timeIndex] = 1
                startTime = self._timeIndex
                currentValue = self._dataCenter.getClosePrice(self._timeIndex)

                stoplossValue = self.getNewStopLoss('buy')

                inTimeTransaction, benefit, didLiquid, didStopLossReach = self._trader.placeOrder(
                    tradingType='buy',
                    timeIndex=self._timeIndex,
                    cryptoName='BTC-USD',
                    amount=investmentPerTrade / currentValue,
                    leverage=self._leverage,
                    stopLossValue=stoplossValue)

                self._subject.update_capital(benefit)
                self._buyWeakSignalAchievedCounts = 0
                self._sellWeakSignalAchievedCounts = 0
                self._state = 'enter'

                if inTimeTransaction:
                    self._numberOfBuys += 1
                    self._totalInvestment += investmentPerTrade
                    self._orders.append(CryptoOrder(
                        cryptoName='BTC-USD',
                        tradingType='buy',
                        openingValue=self._dataCenter.getClosePrice(startTime),
                        amount=investmentPerTrade / currentValue,
                        leverage=1,
                        startTimeIndex=startTime,
                        closingValue=self._dataCenter.getClosePrice(self._timeIndex),
                        endTimeIndex=self._timeIndex,
                        benefit=benefit,
                        didLiquid=didLiquid,
                        stopLossValue=self._trader.getStoplossValue(),
                        didStoplossReach=didStopLossReach))
                    totalBenefit += benefit

                self._trader.resetTrader()

                # decrement time to let bot start another trade when the last one finished.
                self.decrementTime()

            elif self.verifyTrigger('sell') and not self.verifyTrigger('buy'):
                self._state = 'exit'
                self._buyWeakSignalAchievedCounts = 0
                self._sellWeakSignalAchievedCounts = 0

                investmentPerTrade = self._subject.get_investment_per_trade()
                self._startTradeIndex = self._timeIndex
                self._sellHistory[self._timeIndex] = 1
                startTime = self._timeIndex
                currentValue = self._dataCenter.getClosePrice(self._timeIndex)

                stoplossValue = self.getNewStopLoss('sell')

                inTimeTransaction, benefit, didLiquid, didStopLossReach = self._trader.placeOrder(
                    tradingType='sell',
                    timeIndex=self._timeIndex,
                    cryptoName='BTC-USD',
                    amount=investmentPerTrade / currentValue,
                    leverage=self._leverage,
                    stopLossValue=stoplossValue)

                self._subject.update_capital(benefit)
                self._buyWeakSignalAchievedCounts = 0
                self._sellWeakSignalAchievedCounts = 0
                self._state = 'enter'

                if inTimeTransaction:
                    self._numberOfSells += 1
                    self._totalInvestment += investmentPerTrade
                    self._orders.append(CryptoOrder(
                        cryptoName='BTC-USD',
                        tradingType='sell',
                        openingValue=self._dataCenter.getClosePrice(startTime),
                        amount=investmentPerTrade / currentValue,
                        leverage=1,
                        startTimeIndex=startTime,
                        closingValue=self._dataCenter.getClosePrice(self._timeIndex),
                        endTimeIndex=self._timeIndex,
                        benefit=benefit,
                        didLiquid=didLiquid,
                        stopLossValue=self._trader.getStoplossValue(),
                        didStoplossReach=didStopLossReach))

                    totalBenefit += benefit

                self._trader.resetTrader()

                # decrement time to let bot start another trade when the last one finished.
                self.decrementTime()

            if not self.incrementTime():
                continueTrading = False

        self._endTimeIndex = self._timeIndex
        self._totalBenefit = totalBenefit
        self.updateResults()
        self.updateBenefitSeries()
        return self._results

    def verifyTrigger(self, mode):
        if mode == 'buy':
            if self._dataCenter.getSeriesOf(['buy signals']).iloc[self._timeIndex, 0]:
                return True

        if mode == 'sell':
            if self._dataCenter.getSeriesOf(['sell signals']).iloc[self._timeIndex, 0]:
                return True

        return False

    def decrementTime(self):
        self._timeIndex -= 1

    def verifyProcess(self, tradingType):

        if not self.incrementTime():
            return False, True

        self._trader.updateStoplossValues(self.getNewStopLoss(tradingType))

        if tradingType == 'buy':
            if self.verifyTrigger('sell'):
                return False, False
            else:
                return True, False

        elif tradingType == 'sell':
            if self.verifyTrigger('buy'):
                return False, False
            else:
                return True, False

    def getNewStopLoss(self, tradingType):

        currentValue = self._dataCenter.getSeriesOf('close').iloc[self._timeIndex]

        if tradingType == 'buy':
            # return 0.98 * currentValue
            return 0

        elif tradingType == 'sell':
            # return 1.02 * currentValue
            return 100000

    def getOrders(self):
        return self._orders

    def updateResults(self):
        self._numberOfOrders = len(self._orders)
        self._wons = self.getNumberOfSuccessfulTransactions()
        self._losts = self.getNumberOfLostTransactions()
        self._failures = self.getNumberOfFailedTransactions()
        self._winRate = self._wons / self._numberOfOrders if self._numberOfOrders != 0 else 0
        self._benefitPercent = self._totalBenefit / self._totalInvestment * 100 if self._totalInvestment != 0 else 0
        self._results = {'numberOfWons': self._wons,
                         'numberOfLosts': self._losts,
                         'numberOfFailures': self._failures,
                         'totalBenefit': self._totalBenefit,
                         'winRate': self._winRate,
                         'numberOfBuys': self._numberOfBuys,
                         'numberOfSells': self._numberOfSells,
                         'totalInvestment': self._totalInvestment,
                         'benefitPercent': self._benefitPercent,
                         'numberOfOrders': self._numberOfOrders,
                         'totalBenefitPercent': self._benefitPercent * self._numberOfOrders}

    def getNumberOfSuccessfulTransactions(self):
        didWinCounts = 0
        for order in self._orders:
            if order.didLose() is not True and order.didFail() is not True:
                didWinCounts += 1
        return didWinCounts

    def getNumberOfLostTransactions(self):
        didLoseCounts = 0
        for order in self._orders:
            if order.didLose():
                didLoseCounts += 1
        return didLoseCounts

    def getNumberOfFailedTransactions(self):
        didFailCounts = 0
        for order in self._orders:
            if order.didFail():
                didFailCounts += 1
        return didFailCounts

    def reportResults(self):
        print('trading began @ {} and finished @ {}.'.format(self._startTimeIndex, self._endTimeIndex))
        print(
            'number of transactions: {} (Sells:{} Buys:{}), number of wons: {}, number of losses: {}, number of failed requests: {}, '
            'win rate: {}.'.format(
                self._numberOfOrders,
                self._numberOfSells,
                self._numberOfBuys,
                self._wons,
                self._losts,
                self._failures,
                round(self._winRate, 3)))
        print(
            'total investment: {}, total acquired: {}, average benefit percent: %{}, total benefit percent: %{}'.format(
                self._totalInvestment,
                round(self._totalBenefit, 1),
                round(self._benefitPercent, 3),
                round(self._benefitPercent * self._numberOfOrders, 3)
            ))

    def reportOrdersDetails(self):
        for order in self._orders:
            order.printOrder()

    def updateBenefitSeries(self):
        totalBenefit = 0
        benefitSeries = np.zeros(self._dataCenter.getMaxIndex() + 1)
        currentTimeIndex = 0

        for order in self._orders:

            endTime = order.getEndTimeIndex()

            for i in range(currentTimeIndex, endTime + 1):
                benefitSeries[i] = totalBenefit

            currentTimeIndex = endTime + 1

            benefit = order.getTradingBenefit()

            totalBenefit += benefit

        endOfTheTime = self._dataCenter.getMaxIndex()
        for i in range(currentTimeIndex, endOfTheTime + 1):
            benefitSeries[i] = totalBenefit

        return benefitSeries
