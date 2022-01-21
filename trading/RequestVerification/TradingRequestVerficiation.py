from abc import ABC, abstractmethod


class TradingRequestVerifier:
    def __init__(self, tradingType):
        self._initialVerifier = InitialVerifier()
        self._buyStopLossValueVerifier = BuyStopLossValueVerifier()
        self._sellStopLossValueVerifier = SellStopLossValueVerifier()

        if tradingType.lower() == 'sell':
            self._initialVerifier.setNextVerifier(self._sellStopLossValueVerifier)
            self._verificationChain = self._initialVerifier
        elif tradingType.lower() == 'buy':
            self._initialVerifier.setNextVerifier(self._buyStopLossValueVerifier)
            self._verificationChain = self._initialVerifier

    def verifyRequest(self, requestSpecifications):
        return self._verificationChain.verify(requestSpecifications)


class AbstractTradingRequestVerifier:
    _nextVerifier = None

    def setNextVerifier(self, nextVerifier):
        self._nextVerifier = nextVerifier

    @abstractmethod
    def verify(self, request):
        return self._nextVerifier.verify(request) if self._nextVerifier is not None else True


class InitialVerifier(AbstractTradingRequestVerifier):
    def verify(self, request):
        if (
                ('timeIndex' in request)
                and ('cryptoName' in request)
                and ('amount' in request)
                and ('openingValue' in request)
                and ('leverage' in request)
                and ('stopLossValue' in request)
        ):
            return super().verify(request)
        else:
            print('Trading Request Verification Log :: insufficient data in request set!')
            return False


class BuyStopLossValueVerifier(AbstractTradingRequestVerifier):
    def verify(self, request):
        currentValue = request['openingValue']
        leverage = request['leverage']
        stopLossValue = request['stopLossValue']
        leastStopLossValue = currentValue * (1 - 1 / leverage)

        if stopLossValue < leastStopLossValue:
            print('Trading Request Verification Log :: the stop loss value set, is less than liquid status!')
            return False
        else:
            return super().verify(request)


class SellStopLossValueVerifier(AbstractTradingRequestVerifier):
    def verify(self, request):
        currentValue = request['openingValue']
        leverage = request['leverage']
        stopLossValue = request['stopLossValue']
        mostStopLossValue = currentValue * (1 + 1 / leverage)

        if stopLossValue > mostStopLossValue:
            print('Trading Request Verification Log :: the stop loss value set, is more than liquid status!')
            return False
        else:
            return super().verify(request)
