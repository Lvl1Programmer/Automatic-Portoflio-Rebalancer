import streamlit as st
import sqlite3
import pandas as pd
import numpy as np

# Function to add or initialize the portfolio balance
def update_portfolio_balance(amount):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()

    cursor.execute('SELECT balance FROM portfolio_balance LIMIT 1')
    result = cursor.fetchone()

    if result is None:
        cursor.execute('INSERT INTO portfolio_balance (balance) VALUES (?)', (amount,))
    else:
        cursor.execute('UPDATE portfolio_balance SET balance = balance + ?', (amount,))

    conn.commit()
    conn.close()

# Function to get the current balance
def get_portfolio_balance():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()

    cursor.execute('SELECT balance FROM portfolio_balance LIMIT 1')
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return 0.0

# Function to insert stock codes after validating them against the stock_data table
def insert_stock_codes(stock_codes):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    stocks = stock_codes.split()
    valid_stocks = []

    for stock in stocks:
        cursor.execute('SELECT 1 FROM stock_data WHERE stock = ?', (stock,))
        if cursor.fetchone():
            valid_stocks.append(stock)
        else:
            st.write(f"Invalid stock code: {stock}")

    for stock in valid_stocks:
        cursor.execute('''
            INSERT OR IGNORE INTO positions (stock, position_size)
            VALUES (?, ?)
        ''', (stock, 0))

    conn.commit()
    conn.close()

    st.write(f"Inserted stock codes: {', '.join(valid_stocks)}")

# Function to buy a stock and update the position size and balance
def buy_stock(stock, lots, stock_price):
    shares = lots * 100  # Each lot is 100 shares
    total_cost = shares * stock_price
    current_balance = get_portfolio_balance()

    if total_cost > current_balance:
        st.write(f"Not enough balance to buy {lots} lots of {stock}.")
    else:
        # Update the balance
        update_portfolio_balance(-total_cost)

        # Update the position size (in lots)
        conn = sqlite3.connect('stocks.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE positions
            SET position_size = position_size + ?
            WHERE stock = ?
        ''', (lots, stock))
        conn.commit()
        conn.close()

        st.write(f"Bought {lots} lots ({shares} shares) of {stock} for IDR {total_cost}. New balance: IDR {get_portfolio_balance()}")

# Function to remove a stock code from the positions table
def remove_stock_code(stock):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM positions WHERE stock = ?', (stock,))
    conn.commit()
    conn.close()

    st.write(f"Removed stock code: {stock}")

# Function to get the latest price from the database
def get_stock_price(stock):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT close FROM stock_data WHERE stock = ? ORDER BY date DESC LIMIT 1', (stock,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None

# Streamlit App
st.title("Automated Portfolio Manager")

# Connect to the database
conn = sqlite3.connect('stocks.db')
cursor = conn.cursor()

# Ensure tables exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS positions (
        stock TEXT PRIMARY KEY,
        position_size REAL DEFAULT 0
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolio_balance (
        balance REAL DEFAULT 0.0
    )
''')

# Balance Management
st.header("Manage Portfolio Balance")
balance_action = st.radio("Select an action:", ("Add Balance", "View Balance"))

if balance_action == "Add Balance":
    add_amount = st.number_input("Enter the amount to add (IDR):", min_value=0.0)
    if st.button("Add Balance"):
        update_portfolio_balance(add_amount)
        st.write(f"New balance: IDR {get_portfolio_balance()}")
else:
    st.write(f"Current balance: IDR {get_portfolio_balance()}")

# Stock code insertion
st.header("Add Stock Codes")
stock_codes_input = st.text_input("Enter stock codes (separated by spaces):")
if st.button("Add Stock Codes"):
    insert_stock_codes(stock_codes_input)

# Display current positions
positions_df = pd.read_sql("SELECT * FROM positions", conn)
st.write("Current Positions (in lots):")
st.dataframe(positions_df)

# Buy Stock
st.header("Buy Stock")
if not positions_df.empty:
    stock_to_buy = st.selectbox("Select stock to buy:", positions_df['stock'].tolist())
    lots_to_buy = st.number_input("Enter the number of lots to buy:", min_value=0.0)
    
    # Get the stock price from the database
    stock_price = get_stock_price(stock_to_buy)
    if stock_price is not None:
        st.write(f"Current price of {stock_to_buy}: IDR {stock_price} per share")
        if st.button("Buy Stock"):
            buy_stock(stock_to_buy, lots_to_buy, stock_price)
    else:
        st.write(f"Price data not available for {stock_to_buy}")
else:
    st.write("No stocks in the portfolio to buy.")

# Remove a stock code
st.header("Remove Stock Code")
if not positions_df.empty:
    stock_to_remove = st.selectbox("Select stock to remove:", positions_df['stock'].tolist())
    if st.button("Remove Stock Code"):
        remove_stock_code(stock_to_remove)
else:
    st.write("No stocks in the portfolio to remove.")

# Set Target Allocations only for stocks in the portfolio
st.header("Set Target Allocations")
if not positions_df.empty:
    target_ratios = {}
    for stock in positions_df['stock']:
        ratio = st.number_input(f"Target allocation for {stock}:", min_value=0.0, max_value=1.0, value=0.3)
        target_ratios[stock] = ratio

    # Rebalance button
    if st.button("Rebalance Portfolio"):
        # Create the portfolio DataFrame based on the current positions
        portfolio = pd.DataFrame({
            'Stock': positions_df['stock'],
            'Lots': positions_df['position_size'],
            'Price': [get_stock_price(stock) for stock in positions_df['stock']]
        })

        # Calculate current values
        portfolio['Current Value'] = portfolio['Lots'] * 100 * portfolio['Price']
        total_value = portfolio['Current Value'].sum()
        
        # Calculate target values and lots
        portfolio['Target Value'] = portfolio['Stock'].apply(lambda x: target_ratios[x] * total_value)
        portfolio['Target Lots'] = (portfolio['Target Value'] / (100 * portfolio['Price'])).astype(int)

        portfolio['Lots to Trade'] = portfolio['Target Lots'] - portfolio['Lots']

        st.write("Rebalanced Portfolio (in lots):")
        st.dataframe(portfolio)
else:
    st.write("No stocks in the portfolio to set target allocations or rebalance.")

# Close the connection when done
conn.close()
