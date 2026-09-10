from collections import defaultdict, deque
from decimal import Decimal
from enum import Enum

from order import Market, Order, OrderId, OrderType, Side


class OrderBookErrors(Enum):
    INVALID_PRICE = "INVALID_PRICE"
    INVALID_QUANTITY = "INVALID_QUANTITY"
    INVALID_ORDER_ID = "INVALID_ORDER_ID"
    DUPLICATE_ORDER_ID = "DUPLICATE_ORDER_ID"


class OrderBook:
    def __init__(self, market: Market) -> None:
        self.__market: Market = market
        self.__bids: defaultdict[Decimal, deque[Order]] = defaultdict(deque)
        self.__asks: defaultdict[Decimal, deque[Order]] = defaultdict(deque)
        self.__orders: dict[OrderId, Order] = {}

    def add_order(
        self,
        order_id: OrderId,
        side: Side,
        order_type: OrderType,
        quantity: Decimal,
        price: Decimal | None,
    ) -> Order | OrderBookErrors:

        if quantity <= 0:
            return OrderBookErrors.INVALID_QUANTITY
        elif order_id in self.__orders:
            return OrderBookErrors.DUPLICATE_ORDER_ID

        # Only Limit Orders will be placed in the price-time priority queue
        if order_type == OrderType.LIMIT:
            # Limit Orders should always have a price associated with them
            if price is None or price <= 0:
                return OrderBookErrors.INVALID_PRICE

            order = Order(
                order_id, self.__market, side, OrderType.LIMIT, quantity, price
            )
            self.__orders[order_id] = order

            if side == Side.BUY:
                self.__bids[price].append(order)
            else:
                self.__asks[price].append(order)

            # TODO: Match the Limit Order
            return order

        elif order_type == OrderType.MARKET:
            order = Order(
                order_id, self.__market, side, OrderType.MARKET, quantity, None
            )
            self.__orders[order_id] = order

            # TODO: Match the Market Order
            return order

    def cancel_order(self, order_id: OrderId) -> Order | OrderBookErrors:
        if order_id not in self.__orders:
            return OrderBookErrors.INVALID_ORDER_ID

        order = self.__orders[order_id]

        if order.order_type == OrderType.LIMIT:
            if order.price is None:
                return OrderBookErrors.INVALID_PRICE

            if order.side == Side.BUY:
                self.__bids[order.price].remove(order)
            else:
                self.__asks[order.price].remove(order)

        self.__orders.pop(order_id)
        return order

    @property
    def market(self) -> Market:
        return self.__market
