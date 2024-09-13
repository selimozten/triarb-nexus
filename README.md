# TriArb Nexus

## Advanced Triangular Arbitrage Strategy for Cryptocurrency Trading

TriArb Nexus is a high-performance, event-driven triangular arbitrage strategy built on the Hummingbot framework. It leverages real-time order book analysis and efficient execution to capitalize on price discrepancies across three trading pairs in cryptocurrency markets.

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents

- [Key Features](#key-features)
- [Technical Overview](#technical-overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Performance Optimization](#performance-optimization)
- [Security Considerations](#security-considerations)
- [Logging and Monitoring](#logging-and-monitoring)
- [Error Handling and Resilience](#error-handling-and-resilience)
- [Contributing](#contributing)
- [Future Roadmap](#future-roadmap)
- [Disclaimer](#disclaimer)
- [License](#license)

## Key Features

- Real-time arbitrage opportunity detection using advanced order book analysis
- Dynamic profit calculation considering market depth and fees
- Configurable profit thresholds and risk management parameters
- Automated, high-frequency order execution with retry mechanisms
- Comprehensive logging and performance metrics
- Modular architecture allowing easy extension to multiple exchanges
- Robust error handling and failsafe mechanisms
- Detailed unit and integration testing suite

## Technical Overview

TriArb Nexus employs a sophisticated event-driven architecture to efficiently process market data and execute trades. Key components include:

- **OrderBookAnalyzer**: Utilizes efficient algorithms to analyze order book depth and calculate potential arbitrage opportunities.
- **TriangularArbitrageConfig**: Implements a flexible configuration system using environment variables for easy deployment across different environments.
- **EnhancedTriangularArbitrage**: The core strategy class that orchestrates the arbitrage process, including opportunity detection, order placement, and position management.

The strategy leverages Hummingbot's event system to react to market changes in real-time, ensuring low-latency execution of arbitrage opportunities.

## Project Structure

```
triarb-nexus/
│
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── exceptions.py       # Custom exception classes
│   ├── utils.py            # Utility functions
│   ├── order_book_analyzer.py  # Order book analysis logic
│   └── main.py             # Main strategy implementation
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_utils.py
│   ├── test_order_book_analyzer.py
│   └── test_main.py
│
├── .env.example            # Example environment variable file
├── requirements.txt        # Project dependencies
├── setup.py                # Package and distribution management
└── README.md               # This file
```

## Installation

1. Ensure you have Python 3.7 or later installed.

2. Clone the repository:
   ```
   git clone https://github.com/selimozten/triarb-nexus.git
   cd triarb-nexus
   ```

3. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Copy the `.env.example` file to `.env` and configure your settings:
   ```
   cp .env.example .env
   ```

## Configuration

TriArb Nexus uses environment variables for configuration, allowing for flexible deployment across different environments. Key configuration parameters include:

- `CONNECTOR_NAME`: The exchange connector to use (e.g., "binance", "kucoin")
- `FIRST_PAIR`, `SECOND_PAIR`, `THIRD_PAIR`: The trading pairs for triangular arbitrage
- `HOLDING_ASSET`: The asset to hold between trades
- `MIN_PROFITABILITY`: Minimum profit threshold to execute a trade (in percentage)
- `ORDER_AMOUNT`: Base order amount in the holding asset
- `KILL_SWITCH_ENABLED`: Enables automatic strategy shutdown on significant losses
- `KILL_SWITCH_RATE`: Threshold for kill switch activation

Refer to `config.py` for a complete list of configuration options and their default values.

## Usage

To run TriArb Nexus:

1. Ensure your `.env` file is configured correctly.

2. Execute the main script:
   ```
   python src/main.py
   ```

The strategy will initialize, connect to the specified exchange, and begin monitoring for arbitrage opportunities.

## Testing

TriArb Nexus includes a comprehensive test suite to ensure reliability and correctness. To run the tests:

```
python -m unittest discover tests
```

The test suite includes unit tests for individual components and integration tests that simulate the entire arbitrage process.

## Performance Optimization

TriArb Nexus is designed for high-performance operation:

- Efficient order book analysis algorithms minimize CPU usage
- Asynchronous operations reduce latency in market data processing and order execution
- Caching mechanisms for frequently accessed data improve response times

Further optimizations can be implemented based on specific deployment environments and requirements.

## Security Considerations

- API keys and secrets are managed securely through environment variables
- The strategy implements safeguards against excessive trading and potential losses
- Regular security audits and updates are recommended to ensure the integrity of the system

## Logging and Monitoring

TriArb Nexus employs a robust logging system:

- Detailed logs of market analysis, trade execution, and error events
- Integration with Hummingbot's built-in logging mechanisms
- Easy extension to external monitoring and alerting systems

## Error Handling and Resilience

The strategy includes comprehensive error handling:

- Custom exception classes for specific error scenarios
- Graceful degradation in case of partial system failures
- Automatic retry mechanisms for transient errors
- Kill switch functionality to prevent runaway losses

## Contributing

Contributions to TriArb Nexus are welcome! Please refer to our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Future Roadmap

- Multi-exchange arbitrage capabilities
- Machine learning integration for adaptive profit thresholds
- Advanced risk management features
- Real-time performance dashboard

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Developed with ❤️ by [selimozten](https://github.com/selimozten)