from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    CREATED = "CREATED"
    RESTING = "RESTING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class ExecutionStatus(Enum):
    UNFILLED = "UNFILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"


@dataclass(frozen=True)
class OrderId:
    value: int


@dataclass(frozen=True)
class Market:
    base_asset: str
    quote_asset: str


class Order:
    """Base Order class which outlines an Order."""

    def __init__(
        self,
        order_id: OrderId,
        market: Market,
        side: Side,
        quantity: Decimal,
        timestamp: int,
    ) -> None:
        self.order_id: OrderId = order_id
        self.market: Market = market
        self.side: Side = side

        self.quantity_original: Decimal = quantity
        self.quantity_executed: Decimal = Decimal(0)
        self.quantity_remaining: Decimal = self.quantity_original

        self.order_status: OrderStatus = OrderStatus.CREATED
        self.execution_status: ExecutionStatus = ExecutionStatus.UNFILLED

        self.creation_timestamp: int = timestamp


class LimitOrder(Order):
    """
    An order to BUY or SELL a specified quantity at a specific price or better.
    LIMIT Order will always have a price associated with it.
    """

    def __init__(
        self,
        order_id: OrderId,
        market: Market,
        side: Side,
        quantity: Decimal,
        price: Decimal,
        timestamp: int,
    ) -> None:
        super().__init__(order_id, market, side, quantity, timestamp)
        self.price: Decimal = price


class MarketOrder(Order):
    """
    An order to BUY or SELL a specified quantity immediately at the best available market price.
    Market Order do NOT have a price associated with them
    """

    def __init__(
        self,
        order_id: OrderId,
        market: Market,
        side: Side,
        quantity: Decimal,
        timestamp: int,
    ) -> None:
        super().__init__(order_id, market, side, quantity, timestamp)
