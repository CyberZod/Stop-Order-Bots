# Stop-Order-Bots
Place a stop order based on the last closed candle with any of these bots
How they work -
  For buy bot - entry is placed one pipette above the last closed candle, stop loss is placed one pipette below said candle
  For sell bot - just the opposite of the buy bot
  Lot sizes are calculated with commission in mind so your max risk will also be the same
  Orders are sent our to MT5 and placed

These bots does it all for you regarding stop orders - entry, stop loss, take profit, lot size and order placement
Feel free to tweak the symbol, commission per standard lot, RR and of course, credentials to suit your needs
