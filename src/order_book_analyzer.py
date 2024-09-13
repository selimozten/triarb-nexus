from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Tuple
from hummingbot.connector.connector_base import ConnectorBase
from hummingbot.core.data_type.order_book import OrderBook
from hummingbot.core.data_type.common import TradeType
from utils import get_base_amount_for_quote_volume

class OrderBookAnalyzer(ABC):
    @abstractmethod
    def get_base_amount_for_quote_volume(self, orderbook: OrderBook, quote_volume: Decimal) -> Decimal:
        pass

    @abstractmethod
    def get_order_amount_from_exchanged_amount(self, pair: str, side: TradeType, exchanged_amount: Decimal) -> Decimal:
        pass

class DefaultOrderBookAnalyzer(OrderBookAnalyzer):
    def __init__(self, connector: ConnectorBase):
        self.connector = connector

    def get_base_amount_for_quote_volume(self, orderbook: OrderBook, quote_volume: Decimal) -> Decimal:
        entries = orderbook.ask_entries() if quote_volume > 0 else orderbook.bid_entries()
        return get_base_amount_for_quote_volume(entries, abs(quote_volume))

    def get_order_amount_from_exchanged_amount(self, pair: str, side: TradeType, exchanged_amount: Decimal) -> Decimal:
        orderbook = self.connector.get_order_book(pair)
        if side == TradeType.BUY:
            order_amount = self.get_base_amount_for_quote_volume(orderbook, exchanged_amount)
        else:
            order_amount = exchanged_amount
        return self.connector.quantize_order_amount(pair, order_amount)