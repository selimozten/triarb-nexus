import unittest
from unittest.mock import Mock, patch
from decimal import Decimal
from src.main import EnhancedTriangularArbitrage
from src.config import TriangularArbitrageConfig
from src.exceptions import InvalidTradingPairError

class TestEnhancedTriangularArbitrage(unittest.TestCase):
    def setUp(self):
        self.config = TriangularArbitrageConfig()
        self.strategy = EnhancedTriangularArbitrage(self.config)

    def test_init_strategy(self):
        self.strategy.check_trading_pair = Mock()
        self.strategy.set_trading_pair = Mock()
        self.strategy.set_order_side = Mock()
        
        self.strategy.init_strategy()
        
        self.strategy.check_trading_pair.assert_called_once()
        self.strategy.set_trading_pair.assert_called_once()
        self.strategy.set_order_side.assert_called_once()
        self.assertEqual(self.strategy.status, "ACTIVE")

    def test_check_trading_pair_invalid(self):
        self.strategy.config.first_pair = "BTC-USDT"
        self.strategy.config.second_pair = "ETH-USDT"
        self.strategy.config.third_pair = "BTC-ETH"
        
        with self.assertRaises(InvalidTradingPairError):
            self.strategy.check_trading_pair()

    @patch('src.main.split_trading_pair')
    def test_set_trading_pair(self, mock_split):
        mock_split.side_effect = lambda x: tuple(x.split('-'))
        self.strategy.set_trading_pair()
        self.assertEqual(self.strategy.trading_pair["direct"], ('ADA-USDT', 'BTC-USDT', 'ADA-BTC'))
        self.assertEqual(self.strategy.trading_pair["reverse"], ('ADA-BTC', 'BTC-USDT', 'ADA-USDT'))

    def test_calculate_profit(self):
        self.strategy.order_book_analyzer.get_order_amount_from_exchanged_amount = Mock(return_value=Decimal('1'))
        self.strategy.connector.get_quote_volume_for_base_amount = Mock()
        self.strategy.connector.get_quote_volume_for_base_amount.return_value.result_volume = Decimal('100')
        
        profit, amounts = self.strategy.calculate_profit(
            ('BTC-USDT', 'ETH-BTC', 'ETH-USDT'),
            (True, False, False)
        )
        
        self.assertAlmostEqual(profit, Decimal('397.9'), places=1)
        self.assertEqual(amounts, [Decimal('1'), Decimal('1'), Decimal('1')])

    @patch('src.main.ArbitrageOpportunity')
    def test_find_arbitrage_opportunity(self, mock_opportunity):
        self.strategy.calculate_profit = Mock(side_effect=[
            (Decimal('1.0'), [Decimal('1'), Decimal('1'), Decimal('1')]),
            (Decimal('0.5'), [Decimal('1'), Decimal('1'), Decimal('1')])
        ])
        
        self.strategy.find_arbitrage_opportunity()
        
        mock_opportunity.assert_called_once_with("direct", Decimal('1.0'), [Decimal('1'), Decimal('1'), Decimal('1')])

if __name__ == '__main__':
    unittest.main()