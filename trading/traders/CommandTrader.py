
class CommandTrader:
    def __init__(self, **kwargs):
        self._name = kwargs['name'] if 'name' in kwargs else 'unknownTrader'
        self._id = kwargs['id'] if 'id' in kwargs else 0
        self._dataCenter = kwargs['dataCenter'] if 'dataCenter' in kwargs else None
        self._openingValue = 0
        self._currentValue = 0
        self._tradingType = ''
        self._currentBenefit = 0
        self._traderPercent = 0.0002
        self._stoplossValues = []

    def resetTrader(self):
        self._openingValue = 0
        self._currentValue = 0
        self._tradingType = ''
        self._currentBenefit = 0
        self._stoplossValues.clear()

    def setSubject(self, subject):
        self._subject = subject

    def updateStoplossValues(self, newStoplossValue):
        self._stoplossValues.append(float(newStoplossValue))

    def placeOrder(self, **specifications):
        self._tradingType = specifications['tradingType'] if 'tradingType' in specifications else None
        self._openingValue = self._dataCenter.getClosePrice(
            specifications['timeIndex']) if 'timeIndex' in specifications else None

        if self._openingValue is not None and self._tradingType is not None:
            specifications['openingValue'] = self._openingValue

            # if trv.TradingRequestVerifier(self._tradingType).verifyRequest(specifications):
            if True:
                amount = specifications['amount']
                leverage = specifications['leverage']
                stopLossValue = specifications['stopLossValue']  # TO_Be_REMOVED
                self.updateStoplossValues(stopLossValue)

                while True:
                    continueTransaction, didTimeFinish = self._subject.verifyProcess(self._tradingType)

                    if not didTimeFinish:
                        self.updateCurrentValue()
                        self.updateInvestmentStatus(leverage, amount)
                        if continueTransaction:
                            if self.isLiquid(leverage):
                                return True, 0, True, False

                            if self.isStopLossReached(self.getStoplossValue()):
                                return True, self._currentBenefit, False, True
                        else:
                            return True, self._currentBenefit, False, False
                    else:
                        return False, self._currentBenefit, False, False

            else:
                print('transaction failed.')
                return None
        else:
            print('timeIndex is not set in placed order!')
            return None

    def isLiquid(self, leverage):
        openingValue = self._openingValue
        currentValue = self._currentValue
        tradingType = self._tradingType
        if tradingType == 'sell':
            if currentValue > openingValue * (1 + 1 / leverage):
                return True
        elif tradingType == 'buy':
            if currentValue < openingValue * (1 - 1 / leverage):
                return True
        return False

    def updateInvestmentStatus(self, leverage, amount):
        openingValue = self._openingValue
        currentValue = self._currentValue
        tradingType = self._tradingType
        if tradingType == 'sell':
            self._currentBenefit = amount * (openingValue - currentValue) * leverage - (
                        amount * openingValue) * self._traderPercent
        elif tradingType == 'buy':
            self._currentBenefit = amount * (currentValue - openingValue) * leverage - (
                        amount * openingValue) * self._traderPercent

    def isStopLossReached(self, stopLossValue):
        if self._tradingType == 'sell':
            if self._currentValue >= stopLossValue:
                return True
        elif self._tradingType == 'buy':
            if self._currentValue <= stopLossValue:
                return True
        return False

    def updateCurrentValue(self):
        self._currentValue = self._dataCenter.getClosePrice(self._subject.getCurrentTime())

    def getStoplossValue(self):
        if self._tradingType == 'buy':
            return max(self._stoplossValues)
        elif self._tradingType == 'sell':
            return min(self._stoplossValues)