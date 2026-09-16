from decimal import Decimal

from src.exchange.core.order import (
    ExecutionStatus,
    LimitOrder,
    Market,
    MarketOrder,
    OrderId,
    OrderStatus,
    Side,
)
from src.exchange.core.orderbook import OrderBook
from src.exchange.core.trade import Trade, TradeId


class MatchingEngine:
    def __init__(self, market: Market) -> None:
        self._orderbook = OrderBook(market)
        self._trade_ids_counter = 0

    def process_order(
        self, incoming_order: LimitOrder | MarketOrder
    ) -> list[Trade] | None:
        if isinstance(incoming_order, LimitOrder):
            return self._match_limit_order(incoming_order)

        elif isinstance(incoming_order, MarketOrder):
            return self._match_market_order(incoming_order)

    def _match_limit_order(self, incoming_order: LimitOrder):
        trades = []

        while incoming_order.quantity_remaining > 0:
            if incoming_order.side == Side.BUY:
                best_ask = self._orderbook.get_best_ask_price()

                # No Asks or Selling Price is high -> Nothing to match
                if best_ask is None or incoming_order.price < best_ask:
                    break
                resting_order = self._orderbook.get_best_ask_order()
                trade_price = best_ask
            else:
                best_bid = self._orderbook.get_best_bid_price()

                # No Bids or Buying Price is low -> Nothing to match
                if best_bid is None or incoming_order.price > best_bid:
                    break
                resting_order = self._orderbook.get_best_bid_order()
                trade_price = best_bid

            if resting_order is not None:
                trade_quantity = min(
                    incoming_order.quantity_remaining, resting_order.quantity_remaining
                )

                # Update the Incoming Order
                incoming_order.quantity_remaining -= trade_quantity
                incoming_order.quantity_executed += trade_quantity

                if incoming_order.quantity_remaining == 0:
                    incoming_order.execution_status = ExecutionStatus.FILLED
                    incoming_order.order_status = OrderStatus.COMPLETED
                else:
                    incoming_order.execution_status = ExecutionStatus.PARTIALLY_FILLED

                # Update the Resting Order
                resting_order.quantity_remaining -= trade_quantity
                resting_order.quantity_executed += trade_quantity

                # if the resting limit order is filled then pop it from the queue
                if resting_order.quantity_remaining == 0:
                    resting_order.order_status = OrderStatus.COMPLETED
                    resting_order.execution_status = ExecutionStatus.FILLED
                    self._orderbook.remove_order(resting_order.order_id)
                else:
                    resting_order.execution_status = ExecutionStatus.PARTIALLY_FILLED

                buy_order_id = (
                    incoming_order.order_id
                    if incoming_order.side == Side.BUY
                    else resting_order.order_id
                )
                sell_order_id = (
                    incoming_order.order_id
                    if incoming_order.side == Side.SELL
                    else resting_order.order_id
                )

                trade = self._create_trade(
                    buy_order_id,
                    sell_order_id,
                    trade_quantity,
                    trade_price,
                    timestamp=incoming_order.creation_timestamp,
                )
                trades.append(trade)

        # Incoming Order rests in the orderbook in these 2 cases:
        # - Price Condition Fails, no compatible price to match the order
        # - The opposite side of the book is completely empty
        if incoming_order.quantity_remaining > 0:
            incoming_order.order_status = OrderStatus.RESTING
            self._orderbook.add_order(incoming_order)

        return trades if len(trades) > 0 else None

    def _match_market_order(self, incoming_order: MarketOrder):
        trades = []

        while incoming_order.quantity_remaining > 0:
            if incoming_order.side == Side.BUY:
                best_ask = self._orderbook.get_best_ask_price()

                # No Asks -> Nothing to match
                if best_ask is None:
                    break
                resting_order = self._orderbook.get_best_ask_order()
                trade_price = best_ask
            else:
                best_bid = self._orderbook.get_best_bid_price()

                # No Bids -> Nothing to match
                if best_bid is None:
                    break
                resting_order = self._orderbook.get_best_bid_order()
                trade_price = best_bid

            if resting_order is not None:
                trade_quantity = min(
                    incoming_order.quantity_remaining, resting_order.quantity_remaining
                )

                # Update the Incoming Order
                incoming_order.quantity_remaining -= trade_quantity
                incoming_order.quantity_executed += trade_quantity

                if incoming_order.quantity_remaining == 0:
                    incoming_order.execution_status = ExecutionStatus.FILLED
                    incoming_order.order_status = OrderStatus.COMPLETED
                else:
                    incoming_order.execution_status = ExecutionStatus.PARTIALLY_FILLED

                # Update the Resting Order
                resting_order.quantity_remaining -= trade_quantity
                resting_order.quantity_executed += trade_quantity

                # if the resting limit order is filled then pop it from the queue
                if resting_order.quantity_remaining == 0:
                    resting_order.order_status = OrderStatus.COMPLETED
                    resting_order.execution_status = ExecutionStatus.FILLED
                    self._orderbook.remove_order(resting_order.order_id)
                else:
                    resting_order.execution_status = ExecutionStatus.PARTIALLY_FILLED

                buy_order_id = (
                    incoming_order.order_id
                    if incoming_order.side == Side.BUY
                    else resting_order.order_id
                )
                sell_order_id = (
                    incoming_order.order_id
                    if incoming_order.side == Side.SELL
                    else resting_order.order_id
                )

                trade = self._create_trade(
                    buy_order_id,
                    sell_order_id,
                    trade_quantity,
                    trade_price,
                    timestamp=incoming_order.creation_timestamp,
                )
                trades.append(trade)

        # Market Orders never rest in the orderbook
        #  If there is quantity remaining, it means the opposite side of the
        #  book is completely empty. The unfilled remainder is immediately expired.
        if incoming_order.quantity_remaining > 0:
            incoming_order.order_status = OrderStatus.EXPIRED

        return trades if len(trades) > 0 else None

    def _create_trade(
        self,
        buy_order_id: OrderId,
        sell_order_id: OrderId,
        quantity: Decimal,
        price: Decimal,
        timestamp: int,
    ) -> Trade:
        # Assign trade id and create Trade
        self._trade_ids_counter += 1
        trade_id = TradeId(self._trade_ids_counter)

        trade = Trade(trade_id, buy_order_id, sell_order_id, quantity, price, timestamp)

        return trade
