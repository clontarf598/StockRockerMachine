import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from src.stack_scanner import calculate_rsi, analyze_stock, run_scanner, TICKERS


class TestStackScanner(unittest.TestCase):

    def test_calculate_rsi(self):
        # Test RSI calculation with sample data
        data = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114])
        rsi = calculate_rsi(data)
        # RSI should be 100 for consistently rising prices
        # Take lastvalue of RSI, which should be 100 since all price changes are positive and the average loss is zero.
        self.assertAlmostEqual(rsi.iloc[-1], 100.0, places=1)

    @patch('src.stack_scanner.yf.download')
    def test_analyze_stock_success(self, mock_download):
        # Mock successful data download with conditions met
        closes = [100] * 50 + [102] * 10 + [110]  # SMA50 ~100, last > SMA50
        volumes = [1000000] * 60 + [1600000]  # Volume_MA ~1000000, last > 1.5*MA
        mock_data = pd.DataFrame({
            'Close': closes,
            'Volume': volumes
        })
        mock_download.return_value = mock_data

        result = analyze_stock('AAPL')
        self.assertIsNotNone(result)
        self.assertEqual(result['ticker'], 'AAPL')
        self.assertGreaterEqual(result['score'], 2)  # At least momentum and volume

    @patch('src.stack_scanner.yf.download')
    def test_analyze_stock_insufficient_data(self, mock_download):
        # Mock insufficient data
        mock_data = pd.DataFrame({'Close': [100] * 40, 'Volume': [1000000] * 40})
        mock_download.return_value = mock_data

        result = analyze_stock('AAPL')
        self.assertIsNone(result)

    @patch('src.stack_scanner.yf.download')
    def test_analyze_stock_exception(self, mock_download):
        # Mock exception during download
        mock_download.side_effect = Exception("Download failed")

        result = analyze_stock('AAPL')
        self.assertIsNone(result)

    @patch('src.stack_scanner.analyze_stock')
    @patch('builtins.print')
    def test_run_scanner_no_results(self, mock_print, mock_analyze):
        # Mock analyze_stock to return low scores
        mock_analyze.return_value = {'ticker': 'AAPL', 'score': 1}

        run_scanner()
        mock_print.assert_called_with("Keine starken Setups gefunden")

    @patch('src.stack_scanner.analyze_stock')
    @patch('builtins.print')
    @patch('pandas.DataFrame.to_csv')
    def test_run_scanner_with_results(self, mock_to_csv, mock_print, mock_analyze):
        # Mock analyze_stock to return high scores
        mock_analyze.return_value = {'ticker': 'AAPL', 'price': 150.0, 'rsi': 70.0, 'volume': 2000000, 'score': 3}

        run_scanner()
        # Check that print was called with the header
        calls = [call[0][0] for call in mock_print.call_args_list]
        self.assertIn("\nTop Trading Kandidaten:\n", calls)


if __name__ == '__main__':
    unittest.main()