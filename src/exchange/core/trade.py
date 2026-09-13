from dataclasses import dataclass
from decimal import Decimal

from core.order import OrderId


@dataclass(frozen=True)
class TradeId:
    value: int


class Trade:
    """Represents a finalized execution between two opposite-side orders."""

    def __init__(
        self,
        trade_id: TradeId,
        buy_order_id: OrderId,
        sell_order_id: OrderId,
        quantity: Decimal,
        price: Decimal,
        timestamp: int,
    ) -> None:
        self.trade_id: TradeId = trade_id
        self.buy_order_id: OrderId = buy_order_id
        self.sell_order_id: OrderId = sell_order_id

        self.execution_quantity: Decimal = quantity
        self.price: Decimal = price

        self.execution_timestamp: int = timestamp
