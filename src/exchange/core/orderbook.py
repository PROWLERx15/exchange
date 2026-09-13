from decimal import Decimal
from typing import cast

from sortedcontainers import SortedDict

from core.order import LimitOrder, Market, OrderId, Side


class OrderBook:
    """
    The Orderbook maintains the state of all resting Limit Orders using Price Time Priority.
    """

    def __init__(self, market: Market) -> None:
        self._market: Market = market

        # BIDS & ASKS -> SortedDict[price: Decimal, dict[OrderId, Order]]
        # The inner dict[OrderId, Order] maintains First-In-First-Out (FIFO) time priority.
        # For both Bids & Asks: Price Levels sorted Ascending

        self._bids: SortedDict = SortedDict()
        self._asks: SortedDict = SortedDict()

        # Only LIMIT Orders rest in the Orderbook
        self._resting_orders: dict[OrderId, LimitOrder] = {}

    def add_order(self, order: LimitOrder):

        if order.order_id in self._resting_orders:
            raise ValueError(
                f"Order {order.order_id} is already present in the orderbook"
            )

        if order.side == Side.BUY:
            if order.price not in self._bids:
                # Create price level in bids if it does not exist
                self._bids[order.price] = {}

            self._bids[order.price][order.order_id] = order

        elif order.side == Side.SELL:
            if order.price not in self._asks:
                # Create price level in asks if it does not exist
                self._asks[order.price] = {}

            self._asks[order.price][order.order_id] = order

        # Add order to resting orders
        self._resting_orders[order.order_id] = order

    def cancel_order(self, order_id: OrderId) -> bool:

        if order_id not in self._resting_orders:
            return False

        order = self._resting_orders[order_id]

        if order.side == Side.BUY:
            self._bids[order.price].pop(order.order_id)
            # Delete price level if the queue is empty after order cancellation
            if not self._bids[order.price]:
                del self._bids[order.price]
        else:
            self._asks[order.price].pop(order.order_id)
            # Delete price level if the queue is empty after order cancellation
            if not self._asks[order.price]:
                del self._asks[order.price]

        # Remove the order from resting orders
        self._resting_orders.pop(order_id)

        return True

    def get_best_ask_price(self) -> Decimal | None:
        if not self._asks:
            return None

        (best_ask, _) = self._asks.peekitem(0)
        return cast(Decimal, best_ask)

    def get_best_bid_price(self) -> Decimal | None:
        if not self._bids:
            return None

        (best_bid, _) = self._bids.peekitem(-1)
        return cast(Decimal, best_bid)

    def get_best_ask_order(self) -> LimitOrder | None:
        if not self._asks:
            return None

        (_, best_ask_queue) = self._asks.peekitem(0)

        return next(iter(best_ask_queue.values()))

    def get_best_bid_order(self) -> LimitOrder | None:
        if not self._bids:
            return None

        (_, best_bid_queue) = self._bids.peekitem(-1)

        return next(iter(best_bid_queue.values()))

    def get_resting_order(self, order_id: OrderId) -> LimitOrder | None:
        return self._resting_orders.get(order_id)
        
    @property
    def market(self) -> Market:
        return self._market
