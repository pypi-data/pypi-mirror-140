import typing

import QuantConnect
import QuantConnect.Algorithm
import QuantConnect.Data
import QuantConnect.Data.UniverseSelection
import QuantConnect.DataLibrary.Tests
import QuantConnect.DataSource
import QuantConnect.Orders
import System.Collections.Generic


class QuiverCongressDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class BitcoinMetadataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """
    Example algorithm using Blockchain Bitcoin Metadata as a source of alpha
    In this algorithm, we're trading the supply-demand of the Bitcoin blockchain services will affect its price
    """

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...


class CoarseTiingoNewsUniverseSelectionAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """
    Example algorithm of a custom universe selection using coarse data and adding TiingoNews
    If conditions are met will add the underlying and trade it
    """

    def CoarseSelectionFunction(self, coarse: System.Collections.Generic.IEnumerable[QuantConnect.Data.UniverseSelection.CoarseFundamental]) -> System.Collections.Generic.IEnumerable[QuantConnect.Symbol]:
        ...

    def Initialize(self) -> None:
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...

    def OnSecuritiesChanged(self, changes: QuantConnect.Data.UniverseSelection.SecurityChanges) -> None:
        ...


class TiingoNewsAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """
    Look for positive and negative words in the news article description
    and trade based on the sum of the sentiment
    """

    def Initialize(self) -> None:
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...


class TiingoNewsDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class TradingEconomicsCalendarIndicatorAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """This example algorithm shows how to import and use Trading Economics data."""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    @typing.overload
    def OnData(self, data: QuantConnect.DataSource.TradingEconomicsCalendar) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param data: Trading Economics Calendar object
        """
        ...

    @typing.overload
    def OnData(self, data: QuantConnect.DataSource.TradingEconomicsIndicator) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param data: Trading Economics Indicator object
        """
        ...


class TradingEconomicsAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Trades on interest rate announcements from data provided by Trading Economics"""

    def Initialize(self) -> None:
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...


class TradingEconomicsCalendarDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class CachedFREDDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """This class has no documentation."""

    def Initialize(self) -> None:
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...


class QuiverWallStreetBetsDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """
    Quiver Quantitative is a provider of alternative data.
    This algorithm shows how to consume the QuiverWallStreetBets
    """

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...


class QuiverWallStreetBetsDataDemonstrationAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class BenzingaNewsDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class BenzingaNewsAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """
    Benzinga is a provider of news data. Their news is made in-house
    and covers stock related news such as corporate events.
    """

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...

    def OnSecuritiesChanged(self, changes: QuantConnect.Data.UniverseSelection.SecurityChanges) -> None:
        ...


class USTreasuryYieldCurveDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Demonstration algorithm showing how to use and access U.S. Treasury yield curve data"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        ...


class USTreasuryYieldCurveRateDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class USTreasuryYieldCurveRateAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """This class has no documentation."""

    def Initialize(self) -> None:
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...


class SmartInsiderEventBenchmarkAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """This class has no documentation."""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...


class SmartInsiderIntentionsTransactionsDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class SmartInsiderDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm demonstrating usage of SmartInsider data"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    @typing.overload
    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    @typing.overload
    def OnData(self, data: QuantConnect.DataSource.SmartInsiderTransaction) -> None:
        """
        Insider transaction data will be provided to us here
        
        :param data: Transaction data
        """
        ...

    @typing.overload
    def OnData(self, data: QuantConnect.DataSource.SmartInsiderIntention) -> None:
        """
        Insider intention data will be provided to us here
        
        :param data: Intention data
        """
        ...


class SmartInsiderTransactionAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """This class has no documentation."""

    def CoarseUniverse(self, coarse: System.Collections.Generic.IEnumerable[QuantConnect.Data.UniverseSelection.CoarseFundamental]) -> System.Collections.Generic.IEnumerable[QuantConnect.Symbol]:
        ...

    def Initialize(self) -> None:
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...

    def OnSecuritiesChanged(self, changes: QuantConnect.Data.UniverseSelection.SecurityChanges) -> None:
        ...


class CachedUSEnergyDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """This class has no documentation."""

    def Initialize(self) -> None:
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...


class USEnergyDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class USEnergyInformationAdministrationAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """This example algorithm shows how to import and use Tiingo daily prices data."""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...


class VIXCentralContangoDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class QuiverEventsBetaDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class CachedCBOEDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """This class has no documentation."""

    def Initialize(self) -> None:
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...


class CBOEDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class QuiverWikipediaDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class NasdaqDataLinkDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the Nasdaq Data Link data as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class ExtractAlphaTrueBeatsAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the ExtractAlphaTrueBeats type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class SECReportDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Demonstration algorithm showing how to use and access SEC data"""

    Ticker: str = "AAPL"

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        ...


class SECReportDataDemonstrationAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class SECReport8KAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """This class has no documentation."""

    def CoarseSelector(self, coarse: System.Collections.Generic.IEnumerable[QuantConnect.Data.UniverseSelection.CoarseFundamental]) -> System.Collections.Generic.IEnumerable[QuantConnect.Symbol]:
        ...

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...

    def OnSecuritiesChanged(self, changes: QuantConnect.Data.UniverseSelection.SecurityChanges) -> None:
        ...


class SECReportBenchmarkAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """This class has no documentation."""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, data: QuantConnect.Data.Slice) -> None:
        ...


class EstimizeDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """This example algorithm shows how to import and use Estimize data types."""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    @typing.overload
    def OnData(self, data: QuantConnect.DataSource.EstimizeRelease) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param data: EstimizeRelease object containing the stock release data
        """
        ...

    @typing.overload
    def OnData(self, data: QuantConnect.DataSource.EstimizeEstimate) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param data: EstimizeEstimate object containing the stock release data
        """
        ...

    @typing.overload
    def OnData(self, data: QuantConnect.DataSource.EstimizeConsensus) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param data: EstimizeConsensus object containing the stock release data
        """
        ...


class EstimizeConsensusesEstimatesReleasesDataAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using the custom data type as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...

    def OnOrderEvent(self, orderEvent: QuantConnect.Orders.OrderEvent) -> None:
        """
        Order fill event handler. On an order fill update the resulting information is passed to this method.
        
        :param orderEvent: Order event details containing details of the events
        """
        ...


class CryptoSlamNFTSalesAlgorithm(QuantConnect.Algorithm.QCAlgorithm):
    """Example algorithm using NFT Sales data as a source of alpha"""

    def Initialize(self) -> None:
        """Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized."""
        ...

    def OnData(self, slice: QuantConnect.Data.Slice) -> None:
        """
        OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        
        :param slice: Slice object keyed by symbol containing the stock data
        """
        ...


