import MetaTrader5 as mt5
import time
import math

# Account credentials
login = 407593601
server = 'Exness-MT5Real10'
password = 'Jambform123$'

# Initialize MetaTrader 5
if not mt5.initialize(login=login, server=server, password=password):
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# Select EURUSD
symbol = "EURUSDz"
timeframe = mt5.TIMEFRAME_M1

# Ensure EURUSD is available
if not mt5.symbol_select(symbol, True):
    print("Failed to select symbol")
    mt5.shutdown()
    quit()

# Get the previous candle
candles = mt5.copy_rates_from_pos(symbol, timeframe, 0, 3)
previous_candle = candles[-2]

total = 1.09766

def calculate_pip_distance(price1, price2):
    return abs(price1 - price2) * 100000

# Calculate lot size
def calculate_lot_size(entry, stop_loss, risk=10, commission_per_lot=7):
    pips = calculate_pip_distance(entry, stop_loss)
    
    # Calculate the lot size iteratively
    lot_size = risk / pips
    total_loss = risk + (lot_size * commission_per_lot)
    
    while total_loss > risk:
        lot_size -= 0.01  # Decrease lot size by 0.01
        total_loss = (lot_size * pips) + (lot_size * commission_per_lot)
    
    return round(lot_size, 2)


spread = mt5.symbol_info(symbol).spread * mt5.symbol_info(symbol).point

# Set sell stop order based on the previous candle
entry_price = previous_candle['low'] - 1 * mt5.symbol_info(symbol).point
stop_loss = previous_candle['high'] + 1 * mt5.symbol_info(symbol).point
lot_size = calculate_lot_size(entry_price, stop_loss)
order_type = mt5.ORDER_TYPE_SELL_STOP
order_comment = "Sell stop order"
take_profit = entry_price + 3.75 * (entry_price - stop_loss)

entry_to_total_pips = calculate_pip_distance(entry_price, total)
entry_to_sl_pips = calculate_pip_distance(entry_price, stop_loss)

# Print debug information
print(f"Previous Candle: {previous_candle}")
print(f"Entry Price: {entry_price}")
print(f"Stop Loss: {stop_loss}")
print(f"Lot Size: {lot_size}")

# Ensure lot size is valid
min_lot_size = 0.01
max_lot_size = 100.0  # Adjust this as per your broker's maximum lot size
lot_step = 0.01

if lot_size < min_lot_size:
    lot_size = min_lot_size
elif lot_size > max_lot_size:
    lot_size = max_lot_size

# Adjust lot size to the nearest valid step
lot_size = round(lot_size / lot_step) * lot_step

# Print adjusted lot size
print(f"Adjusted Lot Size: {lot_size}")

# Get current bid and ask prices
symbol_info = mt5.symbol_info_tick(symbol)
if symbol_info is None:
    print("Failed to get symbol info tick")
    mt5.shutdown()
    quit()

bid = symbol_info.bid
ask = symbol_info.ask

print(f"Current Bid: {bid}")
print(f"Current Ask: {ask}")

# Create order request
request = {
    "action": mt5.TRADE_ACTION_PENDING,
    "symbol": symbol,
    "volume": lot_size,
    "type": order_type,
    "price": entry_price,
    "sl": stop_loss,
    "tp": take_profit,
    "deviation": 10,
    "magic": 234001,  # Different magic number to distinguish from buy orders
    "comment": order_comment,
    "type_time": mt5.ORDER_TIME_GTC,  # Use Good 'Til Cancelled
    "type_filling": mt5.ORDER_FILLING_IOC,  # Adjust if necessary
}

# Place order
if entry_to_total_pips >= 1.3 * entry_to_sl_pips:
    # Place the order
    result = mt5.order_send(request)
    
    # Print order result details
    print("Order send result details:")
    print(f"  retcode: {result.retcode}")
    print(f"  deal: {result.deal}")
    print(f"  order: {result.order}")
    print(f"  volume: {result.volume}")
    print(f"  price: {result.price}")
    print(f"  bid: {result.bid}")
    print(f"  ask: {result.ask}")
    print(f"  comment: {result.comment}")
    print(f"  request_id: {result.request_id}")
    print(f"  retcode_external: {result.retcode_external}")
    print(f"  request: {result.request}")

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Order failed, retcode =", result.retcode)
    else:
        print("Order placed successfully")
        
        # Calculate and print the commission
        commission = lot_size * 7  # Assuming $7 commission per lot
        print(f"Commission for this trade: ${commission:.2f}")
else:
    print("Order not placed: Distance condition not met")
    print(f"Distance from total to entry: {entry_to_total_pips:.1f} pips")
    print(f"Distance from entry to stop loss: {entry_to_sl_pips:.1f} pips")
    print(f"Required distance from total to entry: {1.3 * entry_to_sl_pips:.1f} pips")


# Shutdown MetaTrader 5
mt5.shutdown()