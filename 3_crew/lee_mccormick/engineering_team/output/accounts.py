#!/usr/bin/env python3
"""
accounts.py - A simple account management system for a trading simulation platform.
"""

import datetime
from typing import Dict, List, Any


def get_share_price(symbol: str) -> float:
    """Returns the current market price for the given share symbol.
    For testing implementation, returns fixed prices for 'AAPL', 'TSLA', and 'GOOGL'.
    
    Args:
        symbol (str): The stock symbol to get the price for
        
    Returns:
        float: The current price of the share
    """
    prices = {
        'AAPL': 150.0,
        'TSLA': 800.0,
        'GOOGL': 2500.0
    }
    return prices.get(symbol, 0.0)


class Account:
    """A class to manage user account operations, share transactions, and account reporting."""
    
    def __init__(self, username: str, initial_deposit: float) -> None:
        """Initialize a new account with a username and initial deposit.
        
        Args:
            username (str): The username associated with the account
            initial_deposit (float): The initial amount deposited into the account
            
        Raises:
            ValueError: If the initial deposit is not positive
        """
        if initial_deposit <= 0:
            raise ValueError("Initial deposit must be positive")
            
        self.username = username
        self.initial_deposit = initial_deposit
        self.balance = initial_deposit
        self.holdings: Dict[str, int] = {}
        self.transactions: List[Dict[str, Any]] = [{
            'type': 'deposit',
            'amount': initial_deposit,
            'timestamp': datetime.datetime.now()
        }]
    
    def deposit_funds(self, amount: float) -> None:
        """Deposit a specified amount of funds into the account and update transaction history.
        
        Args:
            amount (float): The amount to deposit
            
        Raises:
            ValueError: If the deposit amount is not positive
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
            
        self.balance += amount
        self.transactions.append({
            'type': 'deposit',
            'amount': amount,
            'timestamp': datetime.datetime.now()
        })
    
    def withdraw_funds(self, amount: float) -> bool:
        """Try to withdraw a specified amount of funds from the account.
        
        Args:
            amount (float): The amount to withdraw
            
        Returns:
            bool: True if the withdrawal was successful, False otherwise
            
        Raises:
            ValueError: If the withdrawal amount is not positive
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
            
        if amount > self.balance:
            return False
            
        self.balance -= amount
        self.transactions.append({
            'type': 'withdrawal',
            'amount': amount,
            'timestamp': datetime.datetime.now()
        })
        return True
    
    def buy_shares(self, symbol: str, quantity: int) -> bool:
        """Purchase a specified quantity of shares for a given stock symbol.
        
        Args:
            symbol (str): The stock symbol to buy
            quantity (int): The number of shares to buy
            
        Returns:
            bool: True if the purchase was successful, False otherwise
            
        Raises:
            ValueError: If the quantity is not positive
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        price = get_share_price(symbol)
        total_cost = price * quantity
        
        if total_cost > self.balance:
            return False
            
        self.balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self.transactions.append({
            'type': 'buy',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_cost,
            'timestamp': datetime.datetime.now()
        })
        return True
    
    def sell_shares(self, symbol: str, quantity: int) -> bool:
        """Sell a specified quantity of shares for a given stock symbol.
        
        Args:
            symbol (str): The stock symbol to sell
            quantity (int): The number of shares to sell
            
        Returns:
            bool: True if the sale was successful, False otherwise
            
        Raises:
            ValueError: If the quantity is not positive
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            return False
            
        price = get_share_price(symbol)
        total_value = price * quantity
        
        self.balance += total_value
        self.holdings[symbol] -= quantity
        
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
            
        self.transactions.append({
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_value,
            'timestamp': datetime.datetime.now()
        })
        return True
    
    def calculate_portfolio_value(self) -> float:
        """Calculate and return the total value of shares currently held.
        
        Returns:
            float: The total value of the portfolio
        """
        total_value = 0.0
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            total_value += price * quantity
        return total_value
    
    def calculate_profit_loss(self) -> float:
        """Compute and return the profit or loss based on initial deposit and current portfolio value.
        
        Returns:
            float: The profit or loss amount
        """
        portfolio_value = self.calculate_portfolio_value()
        return self.balance + portfolio_value - self.initial_deposit
    
    def get_holdings(self) -> Dict[str, int]:
        """Return the current holdings for each stock symbol.
        
        Returns:
            dict: A dictionary of holdings
        """
        return self.holdings.copy()
    
    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """Return a list of all transactions made on the account.
        
        Returns:
            list: The transaction history
        """
        return self.transactions.copy()