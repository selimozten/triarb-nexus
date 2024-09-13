# TriArb Nexus

TriArb Nexus is an advanced triangular arbitrage strategy for cryptocurrency trading, built on the Hummingbot framework. It leverages price discrepancies across three trading pairs to execute profitable trades automatically.

## Features

- Real-time arbitrage opportunity detection
- Configurable profit thresholds
- Automatic order execution
- Comprehensive logging and error handling
- Flexible configuration through environment variables
- Safety features including a kill switch

## Project Structure

```
triarb-nexus/
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── exceptions.py
│   ├── utils.py
│   ├── order_book_analyzer.py
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_utils.py
│   ├── test_order_book_analyzer.py
│   └── test_main.py
│
├── .env.example
├── requirements.txt
├── setup.py
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/selimozten/triarb-nexus.git
   cd triarb-nexus
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Copy the `.env.example` file to `.env` and fill in your configuration details:
   ```
   cp .env.example .env
   ```

## Configuration

TriArb Nexus uses environment variables for configuration. You can set these in your `.env` file or directly in your environment. Here are the available options:

- `CONNECTOR_NAME`: The name of the exchange connector (default: "kucoin")
- `FIRST_PAIR`: The first trading pair (default: "ADA-USDT")
- `SECOND_PAIR`: The second trading pair (default: "ADA-BTC")
- `THIRD_PAIR`: The third trading pair (default: "BTC-USDT")
- `HOLDING_ASSET`: The asset to hold between trades (default: "USDT")
- `MIN_PROFITABILITY`: Minimum profitability threshold in percentage (default: "0.5")
- `ORDER_AMOUNT`: Order amount in the holding asset (default: "20")
- `KILL_SWITCH_ENABLED`: Enable/disable the kill switch (default: "True")
- `KILL_SWITCH_RATE`: Kill switch activation threshold in percentage (default: "-2")

## Usage

To run TriArb Nexus, execute the following command:

```
python src/main.py
```

## Testing

To run the test suite, use the following command:

```
python -m unittest discover tests
```

## Contributing

Contributions to TriArb Nexus are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This software is for educational purposes only. Do not risk money which you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

## License

This project is licensed under the MIT License.

## Author

Created by [selimozten](https://github.com/selimozten)