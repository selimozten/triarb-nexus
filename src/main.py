import logging
from decimal import Decimal
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass

from hummingbot.core.data_type.order_candidate import OrderCandidate
from hummingbot.strategy.strategy_base import StrategyBase
from hummingbot.core.event.events import (
    BuyOrderCreatedEvent,
    SellOrderCreatedEvent,
    BuyOrderCompletedEvent,
    SellOrderCompletedEvent,
    MarketOrderFailureEvent,
    OrderFilledEvent,
)
from hummingbot.core.data_type.common import OrderType, TradeType
from hummingbot.core.utils.estimate_fee import estimate_fee

from config import TriangularArbitrageConfig
from exceptions import InvalidTradingPairError, InsufficientBalanceError, OrderPlacementError
from order_book_analyzer import DefaultOrderBookAnalyzer
from utils import split_trading_pair

@dataclass
class ArbitrageOpportunity:
    direction: str
    profit: Decimal
    order_amounts: List[Decimal]

class EnhancedTriangularArbitrage(StrategyBase):
    def __init__(self, config: TriangularArbitrageConfig):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.status: str = "NOT_INIT"
        self.trading_pair: Dict[str, Tuple[str, str, str]] = {}
        self.order_side: Dict[str, Tuple[TradeType, TradeType, TradeType]] = {}
        self.profit: Dict[str, Decimal] = {"direct": Decimal("0"), "reverse": Decimal("0")}
        self.order_amount: Dict[str, List[Decimal]] = {"direct": [], "reverse": []}
        self.profitable_direction: str = ""
        self.place_order_trials_count: int = 0
        self.place_order_trials_limit: int = 10
        self.place_order_failure: bool = False
        self.order_candidate: Optional[OrderCandidate] = None
        self.initial_spent_amount: Decimal = Decimal("0")
        self.total_profit: Decimal = Decimal("0")
        self.total_profit_pct: Decimal = Decimal("0")
        self.markets = {self.config.connector_name: {self.config.first_pair, self.config.second_pair, self.config.third_pair}}
        self.order_book_analyzer = DefaultOrderBookAnalyzer(self.connector)
        self.pending_orders: List[OrderCandidate] = []
        self.current_order_index: int = 0
        self.order_ids: List[str] = []
        self.active_order_id: Optional[str] = None
        self._add_markets(self.markets)

    @property
    def connector(self):
        return self.connectors[self.config.connector_name]

    def on_tick(self):
        if self.status == "NOT_INIT":
            self.init_strategy()
            return

        if self.arbitrage_in_progress():
            return

        if not self.ready_for_new_orders():
            return

        try:
            opportunity = self.find_arbitrage_opportunity()
            if opportunity:
                self.start_arbitrage(opportunity)
        except Exception as e:
            self.logger.error(f"Error in on_tick: {str(e)}")
            self.status = "NOT_ACTIVE"

    def init_strategy(self):
        try:
            self.check_trading_pair()
            self.set_trading_pair()
            self.set_order_side()
            self.status = "ACTIVE"
            self.logger.info("Strategy initialized successfully.")
        except InvalidTradingPairError as e:
            self.logger.error(f"Error initializing strategy: {str(e)}")
            self.status = "NOT_ACTIVE"
        except Exception as e:
            self.logger.error(f"Unexpected error initializing strategy: {str(e)}")
            self.status = "NOT_ACTIVE"

    def check_trading_pair(self):
        assets = set()
        for pair in [self.config.first_pair, self.config.second_pair, self.config.third_pair]:
            base, quote = split_trading_pair(pair)
            assets.update([base, quote])
        if len(assets) != 3 or self.config.holding_asset not in assets:
            raise InvalidTradingPairError(f"Pairs {self.config.first_pair}, {self.config.second_pair}, {self.config.third_pair} "
                                          f"are not suitable for triangular arbitrage!")

    def set_trading_pair(self):
        all_pairs = [self.config.first_pair, self.config.second_pair, self.config.third_pair]
        pairs_with_holding = [pair for pair in all_pairs if self.config.holding_asset in pair]
        if len(pairs_with_holding) < 2:
            raise InvalidTradingPairError("At least two pairs must include the holding asset.")

        pairs_ordered = sorted(all_pairs, key=lambda p: self.config.holding_asset in p, reverse=True)
        self.trading_pair["direct"] = tuple(pairs_ordered)
        self.trading_pair["reverse"] = tuple(reversed(pairs_ordered))

    def set_order_side(self):
        for direction in ["direct", "reverse"]:
            sides = []
            pairs = self.trading_pair[direction]
            current_asset = self.config.holding_asset
            for pair in pairs:
                base, quote = split_trading_pair(pair)
                if base == current_asset:
                    sides.append(TradeType.SELL)
                    current_asset = quote
                elif quote == current_asset:
                    sides.append(TradeType.BUY)
                    current_asset = base
                else:
                    raise InvalidTradingPairError(f"Current asset {current_asset} not in pair {pair}")
            self.order_side[direction] = tuple(sides)

    def find_arbitrage_opportunity(self) -> Optional[ArbitrageOpportunity]:
        direct_profit, direct_amounts = self.calculate_profit(self.trading_pair["direct"], self.order_side["direct"])
        reverse_profit, reverse_amounts = self.calculate_profit(self.trading_pair["reverse"], self.order_side["reverse"])

        self.logger.info(f"Direct profit: {round(direct_profit, 2)}%, Reverse profit: {round(reverse_profit, 2)}%")

        if direct_profit >= self.config.min_profitability and direct_profit >= reverse_profit:
            return ArbitrageOpportunity("direct", direct_profit, direct_amounts)
        elif reverse_profit >= self.config.min_profitability:
            return ArbitrageOpportunity("reverse", reverse_profit, reverse_amounts)
        return None

    def calculate_profit(self, trading_pair: Tuple[str, str, str], order_side: Tuple[TradeType, TradeType, TradeType]) -> Tuple[Decimal, List[Decimal]]:
        exchanged_amount = self.config.order_amount_in_holding_asset
        order_amounts = []

        for i in range(3):
            pair = trading_pair[i]
            side = order_side[i]
            amount = self.order_book_analyzer.get_order_amount_from_exchanged_amount(pair, side, exchanged_amount)
            if amount == Decimal("0"):
                self.logger.debug(f"Order amount on {pair} is too low after quantization.")
                return Decimal("-100"), []
            order_amounts.append(amount)
            exchanged_amount = self.connector.get_quote_volume_for_base_amount(pair, side, amount).result_volume

            fee = estimate_fee(self.config.connector_name, is_maker=False)
            exchanged_amount -= fee.percent * exchanged_amount

        start_amount = self.config.order_amount_in_holding_asset
        end_amount = exchanged_amount
        profit = ((end_amount - start_amount) / start_amount) * 100

        return profit, order_amounts

    def start_arbitrage(self, opportunity: ArbitrageOpportunity):
        self.logger.info(f"Starting arbitrage in {opportunity.direction} direction with expected profit {opportunity.profit}%")
        self.profitable_direction = opportunity.direction
        self.pending_orders = []

        for i in range(3):
            pair = self.trading_pair[opportunity.direction][i]
            side = self.order_side[opportunity.direction][i]
            amount = opportunity.order_amounts[i]
            candidate = self.create_order_candidate(pair, side, amount)
            if candidate is None:
                self.logger.error(f"Could not create order candidate for pair {pair}. Aborting arbitrage.")
                return
            self.pending_orders.append(candidate)

        self.current_order_index = 0
        self.status = "ARBITRAGE_STARTED"
        self.place_next_order()

    def create_order_candidate(self, pair: str, side: TradeType, amount: Decimal) -> Optional[OrderCandidate]:
        price = self.connector.get_price_for_volume(pair, side, amount).result_price
        price_quantized = self.connector.quantize_order_price(pair, Decimal(price))
        amount_quantized = self.connector.quantize_order_amount(pair, Decimal(amount))

        if amount_quantized == Decimal("0"):
            self.logger.info(f"Order amount on {pair} is too low to place an order after quantization.")
            return None

        return OrderCandidate(
            trading_pair=pair,
            is_maker=False,
            order_type=OrderType.MARKET,
            order_side=side,
            amount=amount_quantized,
            price=price_quantized
        )

    def place_next_order(self):
        """
        Places the next order in the arbitrage sequence.
        """
        if self.current_order_index >= len(self.pending_orders):
            self.logger.info("All orders have been placed.")
            self.status = "ACTIVE"
            self.calculate_total_profit()
            return

        candidate = self.pending_orders[self.current_order_index]
        self.order_candidate = candidate
        try:
            success = self.process_candidate(candidate)
            if not success:
                raise OrderPlacementError(f"Failed to process order candidate for {candidate.trading_pair}")
        except OrderPlacementError as e:
            self.logger.error(str(e))
            self.status = "NOT_ACTIVE"
            self.reset_arbitrage()

    def process_candidate(self, order_candidate: OrderCandidate) -> bool:
        """
        Processes an order candidate and places the order.

        :param order_candidate: The order candidate to process
        :return: True if the order was successfully placed, False otherwise
        """
        try:
            adjusted_candidate = self.connector.budget_checker.adjust_candidate(order_candidate, all_or_none=True)
            if adjusted_candidate.amount == Decimal("0"):
                raise OrderPlacementError(f"Adjusted order amount is zero for {order_candidate.trading_pair}.")

            order_id = self.place_order(
                self.config.connector_name,
                adjusted_candidate.trading_pair,
                adjusted_candidate.order_side,
                adjusted_candidate.amount,
                adjusted_candidate.order_type,
                adjusted_candidate.price
            )
            self.order_ids.append(order_id)
            self.active_order_id = order_id
            self.logger.info(f"Placed order {order_id} for {adjusted_candidate.trading_pair}.")
            return True
        except Exception as e:
            self.logger.error(f"Error processing order candidate: {str(e)}")
            return False

    def place_order(self, connector_name: str, trading_pair: str, side: TradeType, 
                    amount: Decimal, order_type: OrderType, price: Decimal) -> str:
        """
        Places an order with the specified parameters.

        :param connector_name: The name of the connector to use
        :param trading_pair: The trading pair for the order
        :param side: The side of the order (BUY or SELL)
        :param amount: The amount of the order
        :param order_type: The type of the order
        :param price: The price of the order
        :return: The order ID of the placed order
        """
        if side == TradeType.BUY:
            order_id = self.buy(connector_name, trading_pair, amount, order_type, price)
        else:
            order_id = self.sell(connector_name, trading_pair, amount, order_type, price)
        return order_id

    def arbitrage_in_progress(self) -> bool:
        """
        Checks if an arbitrage is currently in progress.

        :return: True if an arbitrage is in progress, False otherwise
        """
        return self.status == "ARBITRAGE_STARTED"

    def ready_for_new_orders(self) -> bool:
        """
        Checks if the strategy is ready to place new orders.

        :return: True if ready for new orders, False otherwise
        """
        if self.status != "ACTIVE":
            return False

        available_balance = self.connector.get_available_balance(self.config.holding_asset)
        if available_balance < self.config.order_amount_in_holding_asset:
            self.logger.info(f"{self.config.connector_name} {self.config.holding_asset} balance is too low. Cannot place order.")
            return False

        return True

    def calculate_total_profit(self):
        """
        Calculates the total profit from the completed arbitrage.
        """
        final_balance = self.connector.get_available_balance(self.config.holding_asset)
        self.total_profit = final_balance - self.initial_spent_amount
        self.total_profit_pct = (self.total_profit / self.initial_spent_amount) * 100
        self.logger.info(f"Arbitrage completed. Total profit: {self.total_profit} {self.config.holding_asset} ({self.total_profit_pct}%)")

    def reset_arbitrage(self):
        """
        Resets the arbitrage state.
        """
        self.pending_orders = []
        self.current_order_index = 0
        self.order_ids = []
        self.active_order_id = None
        self.profitable_direction = ""
        self.initial_spent_amount = Decimal("0")

    def did_create_buy_order(self, event: BuyOrderCreatedEvent):
        """
        Handles the event when a buy order is created.

        :param event: The BuyOrderCreatedEvent
        """
        if event.order_id == self.active_order_id:
            self.logger.info(f"Buy order {event.order_id} created for {event.trading_pair}.")

    def did_create_sell_order(self, event: SellOrderCreatedEvent):
        """
        Handles the event when a sell order is created.

        :param event: The SellOrderCreatedEvent
        """
        if event.order_id == self.active_order_id:
            self.logger.info(f"Sell order {event.order_id} created for {event.trading_pair}.")

    def did_complete_buy_order(self, event: BuyOrderCompletedEvent):
        """
        Handles the event when a buy order is completed.

        :param event: The BuyOrderCompletedEvent
        """
        if event.order_id == self.active_order_id:
            self.logger.info(f"Buy order {event.order_id} completed for {event.trading_pair}.")
            self.handle_order_completed()

    def did_complete_sell_order(self, event: SellOrderCompletedEvent):
        """
        Handles the event when a sell order is completed.

        :param event: The SellOrderCompletedEvent
        """
        if event.order_id == self.active_order_id:
            self.logger.info(f"Sell order {event.order_id} completed for {event.trading_pair}.")
            self.handle_order_completed()

    def handle_order_completed(self):
        """
        Handles the completion of an order and prepares for the next order.
        """
        self.active_order_id = None
        self.current_order_index += 1
        self.place_next_order()

    def did_fail_order(self, event: MarketOrderFailureEvent):
        """
        Handles the event when an order fails.

        :param event: The MarketOrderFailureEvent
        """
        if event.order_id == self.active_order_id:
            self.logger.error(f"Order {event.order_id} failed for {event.trading_pair}. Aborting arbitrage.")
            self.status = "NOT_ACTIVE"
            self.active_order_id = None
            self.reset_arbitrage()

    def did_fill_order(self, event: OrderFilledEvent):
        """
        Handles the event when an order is filled.

        :param event: The OrderFilledEvent
        """
        if event.order_id == self.active_order_id:
            self.logger.info(f"Order {event.order_id} filled for {event.trading_pair}. Amount: {event.amount}, Price: {event.price}")

    def format_status(self) -> str:
        """
        Formats the current status of the strategy.

        :return: A formatted string representing the current status
        """
        lines = []
        lines.append(f"Status: {self.status}")
        if self.status == "ARBITRAGE_STARTED":
            lines.append(f"Current order index: {self.current_order_index}")
            if self.active_order_id:
                lines.append(f"Active order ID: {self.active_order_id}")
        lines.append(f"Total profit: {self.total_profit} {self.config.holding_asset}")
        lines.append(f"Total profit percentage: {self.total_profit_pct}%")
        return "\n".join(lines)

    def stop(self, clock: Optional[Clock] = None):
        """
        Stops the strategy and cancels any active orders.

        :param clock: The clock used by the strategy (optional)
        """
        self.logger.info("Stopping Enhanced Triangular Arbitrage strategy...")
        if self.active_order_id:
            self.cancel(self.config.connector_name, self.active_order_id)
            self.logger.info(f"Cancelled active order: {self.active_order_id}")
        self.reset_arbitrage()
        super().stop(clock)