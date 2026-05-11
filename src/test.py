import asyncio

import websockets

import socketio

import json

import time


# --- CONFIGURATION ---

BINANCE_WS_URL = "wss://fstream.binance.com/ws/tonusdt@bookTicker" 

COINDCX_SOCKET_URL = "wss://stream.coindcx.com"

COINDCX_CHANNEL = "B-TON_USDT@prices-futures"


# Shared Memory State

binance_live_price = 0.0

# Dictionary to remember exactly when Binance hit a specific price

binance_price_history = {} 


sio = socketio.AsyncClient(logger=False, engineio_logger=False)


@sio.event

async def connect():

 print("\n[COINDCX] Connected. Subscribing to LTP stream...")

 await sio.emit('join', {'channelName': COINDCX_CHANNEL})


@sio.on('price-change')

async def on_coindcx_price(response):

 global binance_live_price, binance_price_history

 us_timestamp = time.time_ns() // 1000 

 

 try:

  # Safe JSON parse for the Double-JSON trap

  if isinstance(response, dict) and 'data' in response:

   inner_data = json.loads(response['data'])

   coindcx_price = float(inner_data.get('p', 0))

   

   if coindcx_price > 0 and binance_live_price > 0:

    # 1. CALCULATE TICK SPREAD (1 Tick = 0.0001)

    price_diff = binance_live_price - coindcx_price

    tick_spread = round(price_diff * 10000) 

    

    # 2. CALCULATE TIME LAG (With Ghost Filter)

    lag_ms = 0

    if coindcx_price in binance_price_history:

     binance_time = binance_price_history[coindcx_price]

     raw_lag_ms = (us_timestamp - binance_time) / 1000.0

     

     # THE FIX: If the lag is over 1,000ms (1 sec), it's a Ghost Timestamp from an old move.

     if raw_lag_ms < 1000:

      lag_ms = raw_lag_ms

    

    # --- TERMINAL HUD OUTPUT ---

    if abs(tick_spread) >= 23:

     print(f"\n🚨 ARB WINDOW OPEN 🚨")

     print(f"BINANCE: {binance_live_price:.4f} | COINDCX: {coindcx_price:.4f}")

     print(f"SPREAD:  {abs(tick_spread)} Ticks")

     if lag_ms > 0:

      print(f"LAG:  {lag_ms:.2f} ms")

     else:

      print(f"LAG:  [Stale Quote / No recent match]")

     print("-" * 40)

    else:

     # Just print a quiet single line to show it's working

     print(f"[SYNCED] BIN: {binance_live_price:.4f} | DCX: {coindcx_price:.4f} | Spread: {abs(tick_spread)} ticks", end="\r")


 except Exception as e:

  pass # Ignore malformed packets


async def watch_binance():

 global binance_live_price, binance_price_history

 async with websockets.connect(BINANCE_WS_URL) as ws:

  print("[BINANCE] Connected. Streaming Best Bids...")

  

  while True:

   msg = await ws.recv()

   us_timestamp = time.time_ns() // 1000 

   

   data = json.loads(msg)

   current_price = float(data['b'])

   

   # Update live state

   binance_live_price = current_price

   

   # Record the timestamp for this price (keep memory small, last 100 prices)

   binance_price_history[current_price] = us_timestamp

   if len(binance_price_history) > 100:

    # Pop the oldest key to stop RAM from overflowing

    oldest_key = next(iter(binance_price_history))

    del binance_price_history[oldest_key]


async def main():

 print("Initiating Live Arbitrage HUD... 🕵️‍♂️💻\n")

 

 binance_task = asyncio.create_task(watch_binance())

 await sio.connect(COINDCX_SOCKET_URL, transports='websocket')

 

 await asyncio.gather(binance_task, sio.wait())


if __name__ == "__main__":

 try:

  asyncio.run(main())

 except KeyboardInterrupt:

  print("\n[SYSTEM] HUD Offline.")

 