class CryptoOrder:
    def __init__(self, **kwargs):
        self._cryptoName = kwargs['cryptoName'] if 'cryptoName' in kwargs else 'UnknownCrypto'
        self._openingValue = kwargs['openingValue'] if 'openingValue' in kwargs else None
        self._amount = kwargs['amount'] if 'amount' in kwargs else None
        self._leverage = kwargs['leverage'] if 'leverage' in kwargs else None
        self._startTimeIndex = kwargs['startTimeIndex'] if 'startTimeIndex' in kwargs else None
        self._closingValue = kwargs['closingValue'] if 'closingValue' in kwargs else None
        self._endTimeIndex = kwargs['endTimeIndex'] if 'endTimeIndex' in kwargs else None
        self._benefit = kwargs['benefit'] if 'benefit' in kwargs else None
        self._didLiquid = kwargs['didLiquid'] if 'didLiquid' in kwargs else None
        self._stopLossValue = kwargs['stopLossValue'] if 'stopLossValue' in kwargs else None
        self._didFail = kwargs['didFail'] if 'didFail' in kwargs else None
        self._tradingType = kwargs['tradingType'] if 'tradingType' in kwargs else 'unknown'
        self._didStoplossReach = kwargs['didStoplossReach'] if 'didStoplossReach' in kwargs else None

    def getDidStoplossReach(self):
        return self._didStoplossReach

    def printOrder(self):
        if self._tradingType == 'sell':
            print('> Transaction Report <SELL> ...')
        elif self._tradingType == 'buy':
            print('> Transaction Report <BUY> ...')

        print('transaction began on crypto:{} @ {} and finished @ {}.'.format(self._cryptoName, self._startTimeIndex,
                                                                              self._endTimeIndex))
        print('started in -> amount: {}, opening value: {}, leverage: {}, stop loss value: {}.'.format(self._amount,
                                                                                                       self._openingValue,
                                                                                                       self._leverage,
                                                                                                       self._stopLossValue))
        print('finished in -> closing value: {}, benefit: {}, did liquid?: {}'.format(self._closingValue, self._benefit,
                                                                                      self._didLiquid))

    def didLose(self):
        if self._didLiquid or self._benefit <= 0:
            return True
        else:
            return False

    def didFail(self):
        if self._didFail:
            return True
        else:
            return False

    def getTradingType(self):
        return self._tradingType

    def getTradingBenefit(self):
        return self._benefit

    def getStartTimeIndex(self):
        return self._startTimeIndex

    def getEndTimeIndex(self):
        return self._endTimeIndex
