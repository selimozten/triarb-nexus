import unittest
from decimal import Decimal
from src.utils import split_trading_pair, get_base_amount_for_quote_volume

class TestUtils(unittest.TestCase):
    def test_split_trading_pair(self):
        self.assertEqual(split_trading_pair('BTC-USDT'), ('BTC', 'USDT'))
        self.assertEqual(split_trading_pair('ETH-BTC'), ('ETH', 'BTC'))
        with self.assertRaises(ValueError):
            split_trading_pair('INVALID')

    def test_get_base_amount_for_quote_volume(self):
        orderbook_entries = [
            (Decimal('100'), Decimal('1')),  # price, amount
            (Decimal('101'), Decimal('2')),
            (Decimal('102'), Decimal('3')),
        ]
        self.assertAlmostEqual(
            get_base_amount_for_quote_volume(orderbook_entries, Decimal('150')),
            Decimal('1.495'), places=3
        )
        self.assertAlmostEqual(
            get_base_amount_for_quote_volume(orderbook_entries, Decimal('500')),
            Decimal('5'), places=3
        )