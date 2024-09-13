from decimal import Decimal
from typing import Tuple, List
from hummingbot.connector.connector_base import ConnectorBase

def split_trading_pair(trading_pair: str) -> Tuple[str, str]:
    return tuple(trading_pair.split('-'))

def get_base_amount_for_quote_volume(orderbook_entries: List[Tuple[Decimal, Decimal]], quote_volume: Decimal) -> Decimal:
    cumulative_volume = Decimal('0')
    cumulative_base_amount = Decimal('0')

    for price, amount in orderbook_entries:
        row_volume = amount * price
        if row_volume + cumulative_volume >= quote_volume:
            row_volume = quote_volume - cumulative_volume
            row_amount = row_volume / price
        else:
            row_amount = amount
        cumulative_volume += row_volume
        cumulative_base_amount += row_amount
        if cumulative_volume >= quote_volume:
            break

    return cumulative_base_amount