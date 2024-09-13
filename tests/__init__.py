import unittest
from unittest.mock import Mock, patch
from decimal import Decimal

# TODO: add any common test utilities or setup functions here
def setup_test_config():
    """
    Creates a test configuration with default values.
    This can be used across different test files.
    """
    from src.config import TriangularArbitrageConfig
    return TriangularArbitrageConfig()

# TODO: define any cleanup operations that need to run after all tests
def teardown_tests():
    """
    Perform any necessary cleanup after running all tests.
    """
    pass  # Add cleanup operations if needed

# TODO: define common mock objects or fixtures here
mock_connector = Mock()
mock_connector.get_order_book.return_value = Mock()
mock_connector.quantize_order_amount.return_value = Decimal('1.0')
mock_connector.quantize_order_price.return_value = Decimal('100.0')