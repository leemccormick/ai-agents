#!/usr/bin/env python3
"""
app.py - A simple Gradio UI for the accounts.py trading simulation platform.
"""

import gradio as gr
from accounts import Account, get_share_price
import pandas as pd
import datetime

# Global account variable - simple for demo purposes
current_account = None

def create_account(username, initial_deposit):
    """Create a new trading account"""
    global current_account
    
    try:
        initial_deposit = float(initial_deposit)
        current_account = Account(username, initial_deposit)
        return f"Account created for {username} with initial deposit of ${initial_deposit:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def deposit_funds(amount):
    """Deposit funds into the account"""
    global current_account
    
    if current_account is None:
        return "Please create an account first"
    
    try:
        amount = float(amount)
        current_account.deposit_funds(amount)
        return f"Successfully deposited ${amount:.2f}. New balance: ${current_account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def withdraw_funds(amount):
    """Withdraw funds from the account"""
    global current_account
    
    if current_account is None:
        return "Please create an account first"
    
    try:
        amount = float(amount)
        if current_account.withdraw_funds(amount):
            return f"Successfully withdrew ${amount:.2f}. New balance: ${current_account.balance:.2f}"
        else:
            return f"Insufficient funds. Current balance: ${current_account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def buy_shares(symbol, quantity):
    """Buy shares of a stock"""
    global current_account
    
    if current_account is None:
        return "Please create an account first"
    
    try:
        quantity = int(quantity)
        symbol = symbol.upper()
        price = get_share_price(symbol)
        
        if price == 0.0:
            return f"Invalid symbol: {symbol}. Available symbols are AAPL, TSLA, GOOGL."
        
        if current_account.buy_shares(symbol, quantity):
            return f"Successfully bought {quantity} shares of {symbol} at ${price:.2f} each."
        else:
            total_cost = price * quantity
            return f"Insufficient funds. Required: ${total_cost:.2f}, Available: ${current_account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def sell_shares(symbol, quantity):
    """Sell shares of a stock"""
    global current_account
    
    if current_account is None:
        return "Please create an account first"
    
    try:
        quantity = int(quantity)
        symbol = symbol.upper()
        
        if current_account.sell_shares(symbol, quantity):
            price = get_share_price(symbol)
            return f"Successfully sold {quantity} shares of {symbol} at ${price:.2f} each."
        else:
            holdings = current_account.get_holdings()
            current_quantity = holdings.get(symbol, 0)
            return f"Insufficient shares. You have {current_quantity} shares of {symbol}."
    except ValueError as e:
        return f"Error: {str(e)}"

def get_account_summary():
    """Get a summary of the account status"""
    global current_account
    
    if current_account is None:
        return "Please create an account first"
    
    portfolio_value = current_account.calculate_portfolio_value()
    profit_loss = current_account.calculate_profit_loss()
    
    summary = f"Account Summary for {current_account.username}\n"
    summary += f"Cash Balance: ${current_account.balance:.2f}\n"
    summary += f"Portfolio Value: ${portfolio_value:.2f}\n"
    summary += f"Total Value: ${(current_account.balance + portfolio_value):.2f}\n"
    
    if profit_loss >= 0:
        summary += f"Profit: ${profit_loss:.2f}\n"
    else:
        summary += f"Loss: ${-profit_loss:.2f}\n"
    
    holdings = current_account.get_holdings()
    if holdings:
        summary += "\nCurrent Holdings:\n"
        for symbol, quantity in holdings.items():
            price = get_share_price(symbol)
            value = price * quantity
            summary += f"- {symbol}: {quantity} shares at ${price:.2f} = ${value:.2f}\n"
    else:
        summary += "\nNo current holdings."
    
    return summary

def get_transaction_history():
    """Get the transaction history of the account"""
    global current_account
    
    if current_account is None:
        return "Please create an account first"
    
    transactions = current_account.get_transaction_history()
    
    if not transactions:
        return "No transactions found."
    
    history = []
    for t in transactions:
        timestamp = t['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        if t['type'] == 'deposit':
            history.append({
                'Timestamp': timestamp,
                'Type': 'Deposit',
                'Amount': f"${t['amount']:.2f}",
                'Details': 'Cash deposit'
            })
        elif t['type'] == 'withdrawal':
            history.append({
                'Timestamp': timestamp,
                'Type': 'Withdrawal',
                'Amount': f"${t['amount']:.2f}",
                'Details': 'Cash withdrawal'
            })
        elif t['type'] == 'buy':
            history.append({
                'Timestamp': timestamp,
                'Type': 'Buy',
                'Amount': f"${t['total']:.2f}",
                'Details': f"Bought {t['quantity']} {t['symbol']} at ${t['price']:.2f}"
            })
        elif t['type'] == 'sell':
            history.append({
                'Timestamp': timestamp,
                'Type': 'Sell',
                'Amount': f"${t['total']:.2f}",
                'Details': f"Sold {t['quantity']} {t['symbol']} at ${t['price']:.2f}"
            })
    
    df = pd.DataFrame(history)
    return df

def check_stock_price(symbol):
    """Check the current price of a stock"""
    symbol = symbol.upper()
    price = get_share_price(symbol)
    
    if price == 0.0:
        return f"Invalid symbol: {symbol}. Available symbols are AAPL, TSLA, GOOGL."
    else:
        return f"Current price of {symbol}: ${price:.2f}"

with gr.Blocks(title="Trading Simulation Platform") as demo:
    gr.Markdown("# Trading Simulation Platform")
    
    with gr.Tab("Account Management"):
        with gr.Group():
            gr.Markdown("### Create Account")
            with gr.Row():
                username_input = gr.Textbox(label="Username")
                initial_deposit_input = gr.Textbox(label="Initial Deposit ($)")
            create_btn = gr.Button("Create Account")
            create_output = gr.Textbox(label="Result")
            create_btn.click(create_account, [username_input, initial_deposit_input], create_output)
        
        with gr.Group():
            gr.Markdown("### Deposit & Withdraw Funds")
            with gr.Row():
                deposit_input = gr.Textbox(label="Deposit Amount ($)")
                deposit_btn = gr.Button("Deposit")
            with gr.Row():
                withdraw_input = gr.Textbox(label="Withdraw Amount ($)")
                withdraw_btn = gr.Button("Withdraw")
            funds_output = gr.Textbox(label="Result")
            deposit_btn.click(deposit_funds, deposit_input, funds_output)
            withdraw_btn.click(withdraw_funds, withdraw_input, funds_output)
    
    with gr.Tab("Trading"):
        with gr.Group():
            gr.Markdown("### Check Stock Price")
            with gr.Row():
                price_check_input = gr.Textbox(label="Stock Symbol")
                price_check_btn = gr.Button("Check Price")
            price_output = gr.Textbox(label="Price Information")
            price_check_btn.click(check_stock_price, price_check_input, price_output)
        
        with gr.Group():
            gr.Markdown("### Buy & Sell Shares")
            with gr.Row():
                buy_symbol_input = gr.Textbox(label="Symbol")
                buy_quantity_input = gr.Textbox(label="Quantity")
                buy_btn = gr.Button("Buy Shares")
            with gr.Row():
                sell_symbol_input = gr.Textbox(label="Symbol")
                sell_quantity_input = gr.Textbox(label="Quantity")
                sell_btn = gr.Button("Sell Shares")
            trade_output = gr.Textbox(label="Result")
            buy_btn.click(buy_shares, [buy_symbol_input, buy_quantity_input], trade_output)
            sell_btn.click(sell_shares, [sell_symbol_input, sell_quantity_input], trade_output)
    
    with gr.Tab("Portfolio"):
        with gr.Group():
            gr.Markdown("### Account Summary")
            summary_btn = gr.Button("Get Account Summary")
            summary_output = gr.Textbox(label="Account Summary")
            summary_btn.click(get_account_summary, inputs=None, outputs=summary_output)
        
        with gr.Group():
            gr.Markdown("### Transaction History")
            history_btn = gr.Button("Get Transaction History")
            history_output = gr.DataFrame(label="Transaction History")
            history_btn.click(get_transaction_history, inputs=None, outputs=history_output)

if __name__ == "__main__":
    demo.launch()