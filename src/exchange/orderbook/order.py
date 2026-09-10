import time
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"


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
    def __init__(
        self,
        order_id: OrderId,
        market: Market,
        side: Side,
        order_type: OrderType,
        quantity: Decimal,
        price: Decimal | None = None,
    ) -> None:
        self.order_id: OrderId = order_id
        self.market: Market = market
        self.side: Side = side
        self.order_type: OrderType = order_type
        self.price = price

        self.quantity_original: Decimal = quantity
        self.quantity_executed: Decimal = Decimal(0)
        self.quantity_remaining: Decimal = self.quantity_original

        self.order_status: OrderStatus = OrderStatus.CREATED
        self.execution_status: ExecutionStatus = ExecutionStatus.UNFILLED

        self.creation_timestamp: int = time.time_ns()
