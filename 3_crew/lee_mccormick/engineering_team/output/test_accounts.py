#!/usr/bin/env python3
"""
test_accounts.py - Unit tests for the accounts.py module.
"""

import unittest
from unittest import mock
import datetime

import accounts


class TestGetSharePrice(unittest.TestCase):
    """Test cases for the get_share_price function."""
    
    def test_get_share_price_known_symbols(self):
        """Test that get_share_price returns correct prices for known symbols."""
        self.assertEqual(accounts.get_share_price('AAPL'), 150.0)
        self.assertEqual(accounts.get_share_price('TSLA'), 800.0)
        self.assertEqual(accounts.get_share_price('GOOGL'), 2500.0)
    
    def test_get_share_price_unknown_symbol(self):
        """Test that get_share_price returns 0.0 for unknown symbols."""
        self.assertEqual(accounts.get_share_price('UNKNOWN'), 0.0)


class TestAccount(unittest.TestCase):
    """Test cases for the Account class."""
    
    def setUp(self):
        """Set up a test account before each test."""
        self.username = 'testuser'
        self.initial_deposit = 10000.0
        self.account = accounts.Account(self.username, self.initial_deposit)
    
    def test_init_valid(self):
        """Test account initialization with valid parameters."""
        self.assertEqual(self.account.username, self.username)
        self.assertEqual(self.account.initial_deposit, self.initial_deposit)
        self.assertEqual(self.account.balance, self.initial_deposit)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.transactions[0]['type'], 'deposit')
        self.assertEqual(self.account.transactions[0]['amount'], self.initial_deposit)
    
    def test_init_invalid_deposit(self):
        """Test account initialization with invalid initial deposit."""
        with self.assertRaises(ValueError):
            accounts.Account(self.username, 0)
        with self.assertRaises(ValueError):
            accounts.Account(self.username, -100)
    
    def test_deposit_funds_valid(self):
        """Test depositing valid amount of funds."""
        deposit_amount = 500.0
        initial_balance = self.account.balance
        initial_transaction_count = len(self.account.transactions)
        
        self.account.deposit_funds(deposit_amount)
        
        self.assertEqual(self.account.balance, initial_balance + deposit_amount)
        self.assertEqual(len(self.account.transactions), initial_transaction_count + 1)
        latest_transaction = self.account.transactions[-1]
        self.assertEqual(latest_transaction['type'], 'deposit')
        self.assertEqual(latest_transaction['amount'], deposit_amount)
    
    def test_deposit_funds_invalid(self):
        """Test depositing invalid amounts."""
        with self.assertRaises(ValueError):
            self.account.deposit_funds(0)
        with self.assertRaises(ValueError):
            self.account.deposit_funds(-100)
    
    def test_withdraw_funds_valid(self):
        """Test withdrawing valid amount of funds."""
        withdraw_amount = 500.0
        initial_balance = self.account.balance
        initial_transaction_count = len(self.account.transactions)
        
        result = self.account.withdraw_funds(withdraw_amount)
        
        self.assertTrue(result)
        self.assertEqual(self.account.balance, initial_balance - withdraw_amount)
        self.assertEqual(len(self.account.transactions), initial_transaction_count + 1)
        latest_transaction = self.account.transactions[-1]
        self.assertEqual(latest_transaction['type'], 'withdrawal')
        self.assertEqual(latest_transaction['amount'], withdraw_amount)
    
    def test_withdraw_funds_insufficient(self):
        """Test withdrawing more than balance."""
        withdraw_amount = self.account.balance + 100
        initial_balance = self.account.balance
        initial_transaction_count = len(self.account.transactions)
        
        result = self.account.withdraw_funds(withdraw_amount)
        
        self.assertFalse(result)
        self.assertEqual(self.account.balance, initial_balance)
        self.assertEqual(len(self.account.transactions), initial_transaction_count)
    
    def test_withdraw_funds_invalid(self):
        """Test withdrawing invalid amounts."""
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(0)
        with self.assertRaises(ValueError):
            self.account.withdraw_funds(-100)
    
    @mock.patch('accounts.get_share_price')
    def test_buy_shares_success(self, mock_get_price):
        """Test buying shares successfully."""
        mock_get_price.return_value = 100.0
        symbol = 'AAPL'
        quantity = 10
        expected_cost = quantity * 100.0
        initial_balance = self.account.balance
        
        result = self.account.buy_shares(symbol, quantity)
        
        self.assertTrue(result)
        self.assertEqual(self.account.balance, initial_balance - expected_cost)
        self.assertEqual(self.account.holdings.get(symbol), quantity)
        latest_transaction = self.account.transactions[-1]
        self.assertEqual(latest_transaction['type'], 'buy')
        self.assertEqual(latest_transaction['symbol'], symbol)
        self.assertEqual(latest_transaction['quantity'], quantity)
        self.assertEqual(latest_transaction['price'], 100.0)
        self.assertEqual(latest_transaction['total'], expected_cost)
    
    @mock.patch('accounts.get_share_price')
    def test_buy_shares_insufficient_funds(self, mock_get_price):
        """Test buying shares with insufficient funds."""
        mock_get_price.return_value = 10000.0
        symbol = 'AAPL'
        quantity = 2
        initial_balance = self.account.balance
        initial_transaction_count = len(self.account.transactions)
        
        result = self.account.buy_shares(symbol, quantity)
        
        self.assertFalse(result)
        self.assertEqual(self.account.balance, initial_balance)
        self.assertEqual(self.account.holdings.get(symbol, 0), 0)
        self.assertEqual(len(self.account.transactions), initial_transaction_count)
    
    def test_buy_shares_invalid_quantity(self):
        """Test buying invalid quantity of shares."""
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', 0)
        with self.assertRaises(ValueError):
            self.account.buy_shares('AAPL', -5)
    
    @mock.patch('accounts.get_share_price')
    def test_sell_shares_success(self, mock_get_price):
        """Test selling shares successfully."""
        mock_get_price.return_value = 100.0
        symbol = 'AAPL'
        buy_quantity = 10
        sell_quantity = 5
        expected_value = sell_quantity * 100.0
        
        # First buy some shares
        self.account.buy_shares(symbol, buy_quantity)
        initial_balance = self.account.balance
        
        result = self.account.sell_shares(symbol, sell_quantity)
        
        self.assertTrue(result)
        self.assertEqual(self.account.balance, initial_balance + expected_value)
        self.assertEqual(self.account.holdings.get(symbol), buy_quantity - sell_quantity)
        latest_transaction = self.account.transactions[-1]
        self.assertEqual(latest_transaction['type'], 'sell')
        self.assertEqual(latest_transaction['symbol'], symbol)
        self.assertEqual(latest_transaction['quantity'], sell_quantity)
        self.assertEqual(latest_transaction['price'], 100.0)
        self.assertEqual(latest_transaction['total'], expected_value)
    
    @mock.patch('accounts.get_share_price')
    def test_sell_shares_all(self, mock_get_price):
        """Test selling all shares of a symbol."""
        mock_get_price.return_value = 100.0
        symbol = 'AAPL'
        quantity = 10
        expected_value = quantity * 100.0
        
        # First buy some shares
        self.account.buy_shares(symbol, quantity)
        initial_balance = self.account.balance
        
        result = self.account.sell_shares(symbol, quantity)
        
        self.assertTrue(result)
        self.assertEqual(self.account.balance, initial_balance + expected_value)
        self.assertNotIn(symbol, self.account.holdings)
    
    def test_sell_shares_insufficient(self):
        """Test selling more shares than owned."""
        symbol = 'AAPL'
        # First buy some shares
        self.account.buy_shares(symbol, 5)
        initial_balance = self.account.balance
        initial_holdings = self.account.get_holdings()
        initial_transaction_count = len(self.account.transactions)
        
        result = self.account.sell_shares(symbol, 10)
        
        self.assertFalse(result)
        self.assertEqual(self.account.balance, initial_balance)
        self.assertEqual(self.account.get_holdings(), initial_holdings)
        self.assertEqual(len(self.account.transactions), initial_transaction_count)
    
    def test_sell_shares_nonexistent(self):
        """Test selling shares that aren't owned."""
        result = self.account.sell_shares('NONEXISTENT', 5)
        self.assertFalse(result)
    
    def test_sell_shares_invalid_quantity(self):
        """Test selling invalid quantity of shares."""
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', 0)
        with self.assertRaises(ValueError):
            self.account.sell_shares('AAPL', -5)
    
    @mock.patch('accounts.get_share_price')
    def test_calculate_portfolio_value_empty(self, mock_get_price):
        """Test calculating portfolio value with no holdings."""
        mock_get_price.return_value = 100.0
        value = self.account.calculate_portfolio_value()
        self.assertEqual(value, 0.0)
    
    @mock.patch('accounts.get_share_price')
    def test_calculate_portfolio_value(self, mock_get_price):
        """Test calculating portfolio value with holdings."""
        # Set up mock to return different values for different symbols
        def side_effect(symbol):
            return {'AAPL': 150.0, 'TSLA': 800.0}.get(symbol, 0.0)
        
        mock_get_price.side_effect = side_effect
        
        # Buy some shares
        self.account.holdings = {'AAPL': 10, 'TSLA': 5}
        
        value = self.account.calculate_portfolio_value()
        expected_value = 10 * 150.0 + 5 * 800.0
        self.assertEqual(value, expected_value)
    
    @mock.patch('accounts.get_share_price')
    def test_calculate_profit_loss_no_change(self, mock_get_price):
        """Test calculating profit/loss with no trades."""
        mock_get_price.return_value = 100.0
        profit_loss = self.account.calculate_profit_loss()
        self.assertEqual(profit_loss, 0.0)
    
    @mock.patch('accounts.get_share_price')
    def test_calculate_profit_loss_with_trades(self, mock_get_price):
        """Test calculating profit/loss after trades."""
        # Set up mock for share prices
        def side_effect(symbol):
            return {'AAPL': 120.0}.get(symbol, 0.0)
        
        mock_get_price.side_effect = side_effect
        
        # Buy some shares at 100 (mocked in buy_shares)
        mock_get_price.return_value = 100.0
        self.account.buy_shares('AAPL', 10)  # Cost: 1000
        
        # Now use our side_effect for portfolio calculation (price: 120)
        mock_get_price.side_effect = side_effect
        
        # Calculate profit/loss: 
        # Initial: 10000
        # Spent: 1000 on AAPL
        # Current balance: 9000
        # Portfolio value: 10 * 120 = 1200
        # P/L = 9000 + 1200 - 10000 = 200
        profit_loss = self.account.calculate_profit_loss()
        self.assertEqual(profit_loss, 200.0)
    
    def test_get_holdings(self):
        """Test getting account holdings."""
        # Initial holdings should be empty
        self.assertEqual(self.account.get_holdings(), {})
        
        # Add some holdings directly
        self.account.holdings = {'AAPL': 10, 'TSLA': 5}
        
        holdings = self.account.get_holdings()
        self.assertEqual(holdings, {'AAPL': 10, 'TSLA': 5})
        
        # Verify that we get a copy, not the original
        holdings['AAPL'] = 20
        self.assertEqual(self.account.holdings['AAPL'], 10)
    
    def test_get_transaction_history(self):
        """Test getting transaction history."""
        # Initial history should have just the deposit
        self.assertEqual(len(self.account.get_transaction_history()), 1)
        
        # Add some transactions
        self.account.deposit_funds(500)
        self.account.withdraw_funds(200)
        
        history = self.account.get_transaction_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['type'], 'deposit')
        self.assertEqual(history[0]['amount'], self.initial_deposit)
        self.assertEqual(history[1]['type'], 'deposit')
        self.assertEqual(history[1]['amount'], 500)
        self.assertEqual(history[2]['type'], 'withdrawal')
        self.assertEqual(history[2]['amount'], 200)
        
        # Verify that we get a copy, not the original
        history[0]['amount'] = 999
        self.assertEqual(self.account.transactions[0]['amount'], self.initial_deposit)


if __name__ == '__main__':
    unittest.main()