import os
from decimal import Decimal
from dataclasses import dataclass

@dataclass
class TriangularArbitrageConfig:
    connector_name: str = os.getenv("CONNECTOR_NAME", "kucoin")
    first_pair: str = os.getenv("FIRST_PAIR", "ADA-USDT")
    second_pair: str = os.getenv("SECOND_PAIR", "ADA-BTC")
    third_pair: str = os.getenv("THIRD_PAIR", "BTC-USDT")
    holding_asset: str = os.getenv("HOLDING_ASSET", "USDT")
    min_profitability: Decimal = Decimal(os.getenv("MIN_PROFITABILITY", "0.5"))
    order_amount_in_holding_asset: Decimal = Decimal(os.getenv("ORDER_AMOUNT", "20"))
    kill_switch_enabled: bool = os.getenv("KILL_SWITCH_ENABLED", "True").lower() == "true"
    kill_switch_rate: Decimal = Decimal(os.getenv("KILL_SWITCH_RATE", "-2"))