import unittest
from unittest.mock import patch
from decimal import Decimal
from src.config import TriangularArbitrageConfig

class TestTriangularArbitrageConfig(unittest.TestCase):
    @patch.dict('os.environ', {
        'CONNECTOR_NAME': 'binance',
        'FIRST_PAIR': 'ETH-USDT',
        'SECOND_PAIR': 'ETH-BTC',
        'THIRD_PAIR': 'BTC-USDT',
        'HOLDING_ASSET': 'USDT',
        'MIN_PROFITABILITY': '0.7',
        'ORDER_AMOUNT': '30',
        'KILL_SWITCH_ENABLED': 'False',
        'KILL_SWITCH_RATE': '-3'
    })
    def test_config_from_env(self):
        config = TriangularArbitrageConfig()
        self.assertEqual(config.connector_name, 'binance')
        self.assertEqual(config.first_pair, 'ETH-USDT')
        self.assertEqual(config.second_pair, 'ETH-BTC')
        self.assertEqual(config.third_pair, 'BTC-USDT')
        self.assertEqual(config.holding_asset, 'USDT')
        self.assertEqual(config.min_profitability, Decimal('0.7'))
        self.assertEqual(config.order_amount_in_holding_asset, Decimal('30'))
        self.assertFalse(config.kill_switch_enabled)
        self.assertEqual(config.kill_switch_rate, Decimal('-3'))

    def test_config_defaults(self):
        config = TriangularArbitrageConfig()
        self.assertEqual(config.connector_name, 'kucoin')
        self.assertEqual(config.first_pair, 'ADA-USDT')
        self.assertEqual(config.second_pair, 'ADA-BTC')
        self.assertEqual(config.third_pair, 'BTC-USDT')
        self.assertEqual(config.holding_asset, 'USDT')
        self.assertEqual(config.min_profitability, Decimal('0.5'))
        self.assertEqual(config.order_amount_in_holding_asset, Decimal('20'))
        self.assertTrue(config.kill_switch_enabled)
        self.assertEqual(config.kill_switch_rate, Decimal('-2'))