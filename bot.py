import logging
import os
import pandas as pd
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Set up logging
logging.basicConfig(level=logging.INFO)

# PRS2 calculation (same as Pine Script logic)
def calculate_prs2(df, length=30, mult=2):
    src = (df['High'] + df['Low'] + df['Close']) / 3
    atr = df['High'].rolling(length).max() - df['Low'].rolling(length).min()
    atr = atr.rolling(length).mean()

    avg = src.copy()
    hold_atr = 0.0
    for i in range(1, len(df)):
        prev_avg = avg.iloc[i-1]
        price = src.iloc[i]
        atr_val = atr.iloc[i] * mult

        if price - prev_avg > atr_val:
            avg.iloc[i] = prev_avg + atr_val
        elif prev_avg - price > atr_val:
            avg.iloc[i] = prev_avg - atr_val
        else:
            avg.iloc[i] = prev_avg

        if avg.iloc[i] != avg.iloc[i-1]:
            hold_atr = atr_val / 2

    prS2 = avg - hold_atr * 2
    return prS2

# Get data and check if stock touched PRS2 and bounced
def check_stock_bounce(ticker):
    df = yf.download(ticker, period="30d", interval="1d")
    if len(df) < 30:
        return False

    prS2 = calculate_prs2(df)
    if df['Low'].iloc[-1] <= prS2.iloc[-1] and df['Close'].iloc[-1] > prS2.iloc[-1]:
        return True
    return False

# Telegram /check command
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Checking Nifty 500 stocks...")
    
    nifty_500 = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS"]  # Sample — add full Nifty 500 list
    matched = []

    for ticker in nifty_500:
        try:
            if check_stock_bounce(ticker):
                matched.append(ticker)
        except Exception as e:
            logging.warning(f"Error checking {ticker}: {e}")

    if matched:
        await update.message.reply_text("📈 Stocks bouncing at PRS2:\n" + "\n".join(matched))
    else:
        await update.message.reply_text("❌ No stocks touched PRS2 today.")

# Bot entry point
if __name__ == '__main__':
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        raise Exception("BOT_TOKEN not found in environment")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("check", check))
    app.run_polling()
