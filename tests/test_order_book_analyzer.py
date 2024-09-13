import unittest
from unittest.mock import Mock, patch
from decimal import Decimal
from src.order_book_analyzer import DefaultOrderBookAnalyzer
from hummingbot.core.data_type.order_book import OrderBook
from hummingbot.core.data_type.order_book_row import OrderBookRow

class TestDefaultOrderBookAnalyzer(unittest.TestCase):
    def setUp(self):
        self.mock_connector = Mock()
        self.analyzer = DefaultOrderBookAnalyzer(self.mock_connector)

    def test_get_base_amount_for_quote_volume(self):
        mock_orderbook = Mock(spec=OrderBook)
        mock_orderbook.ask_entries.return_value = [
            OrderBookRow(Decimal('100'), Decimal('1'), 0),
            OrderBookRow(Decimal('101'), Decimal('2'), 1),
        ]
        result = self.analyzer.get_base_amount_for_quote_volume(mock_orderbook, Decimal('150'))
        self.assertAlmostEqual(result, Decimal('1.495'), places=3)

    @patch('src.order_book_analyzer.get_base_amount_for_quote_volume')
    def test_get_order_amount_from_exchanged_amount(self, mock_get_base_amount):
        mock_get_base_amount.return_value = Decimal('1.5')
        self.mock_connector.get_order_book.return_value = Mock()
        self.mock_connector.quantize_order_amount.return_value = Decimal('1.5')

        result = self.analyzer.get_order_amount_from_exchanged_amount('BTC-USDT', True, Decimal('150'))
        self.assertEqual(result, Decimal('1.5'))

        result = self.analyzer.get_order_amount_from_exchanged_amount('BTC-USDT', False, Decimal('150'))
        self.assertEqual(result, Decimal('1.5'))