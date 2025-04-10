# === 1. 套件載入 ===
import os
import random
import requests
import feedparser
import asyncio
import re
import zhconv
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
)

# === 載入環境變數 ===
load_dotenv()

TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
E3A_ADDRESS = 'EKYotMbZR82JAVakfnaQbRfCE7oyWLsXVwfyjwTRdaos'
CHAT_ID = os.environ.get("CHAT_ID", "-100xxxxxxxxxx")


# === info 指令 ===
async def info(update: Update, context):
    info_text = """📌 *E3A Community Info*

Welcome to EternalAI — your on-chain AI soulmate.

🔗 *Useful Links*  
🌐 Website: [eternalai.io](https://ai.eternalai.io/)  
📄 Whitepaper: [Read here](https://ai.eternalai.io/static/Helloworld.pdf)  
💬 Discord: [Join us](https://discord.com/invite/ZM7EdkCHZP)  
🐦 Twitter: [Follow us](https://x.com/e3a_eternalai)  
🛒 Buy Token: [DexScreener](https://dexscreener.com/solana/EKYotMbZR82JAVakfnaQbRfCE7oyWLsXVwfyjwTRdaos)

📣 *What can I ask the bot?*  
Ask about token stats, price, holders, links, and we’ll respond instantly.

👀 New here? Try `/faq` or ask your first question.
"""
    await update.message.reply_text(info_text, parse_mode="Markdown")


# === 查價格功能 ===
def get_e3a_price():
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={E3A_ADDRESS}"
        res = requests.get(url)
        data = res.json()
        pair = data.get('pairs', [{}])[0]
        return pair.get('priceUsd'), pair.get('marketCap')
    except Exception as e:
        print("價格錯誤：", e)
        return None, None


# === 自動轉發推特貼文（每 5 分鐘） ===
LAST_TWEET_LINK = None

async def tweet_watcher(application):
    global LAST_TWEET_LINK
    RSS_URL = "https://rsshub.app/twitter/user/e3a_eternalai"

    while True:
        feed = feedparser.parse(RSS_URL)
        if feed.entries:
            latest = feed.entries[0]
            tweet_link = latest.link
            tweet_text = latest.title

            if tweet_link != LAST_TWEET_LINK:
                message = f"📢 *New Tweet from EternalAI:*\n\n{tweet_text}\n\n🔗 [View Tweet]({tweet_link})"
                await application.bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode="Markdown",
                    disable_web_page_preview=False
                )
                LAST_TWEET_LINK = tweet_link

        await asyncio.sleep(300)


# === help 指令 ===
async def help_command(update: Update, context):
    help_text = """✅ *E3A Bot Command Menu*

Here are the available commands:
/info - Show community info & links
/help - Show all supported commands
/faq - Frequently Asked Questions
/stats - Show E3A Token price & market cap
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


# === faq 指令 ===
async def faq(update: Update, context):
    text = """❓ *FAQ:*

*Q:* Where to buy E3A?  
*A:* [DexScreener](https://dexscreener.com/solana/EKYotMbZR82JAVakfnaQbRfCE7oyWLsXVwfyjwTRdaos)

*Q:* Total Supply?  
*A:* 1,000,000,000

*Q:* Will it be listed on CEX?  
*A:* Yes, roadmap includes Tier 1 exchange goals.
"""
    await update.message.reply_text(text, parse_mode="Markdown")


# === 情緒偵測 ===
async def emotion_response(msg):
    lower = zhconv.convert(msg.lower(), 'zh-hans')
    if any(keyword in lower for keyword in ["崩潰", "不行了", "想放棄", "虧爆", "跌爛", "爆倉"]):
        return "💡 HODL or DYOR — Crypto is a roller coaster!"
    return None


# === 處理訊息 ===
async def handle_message(update: Update, context):
    print("🧠 handle_message 被觸發")
    msg = update.message.text.lower()

    if any(word in msg for word in ["airdrop", "fakewallet", "詐騙", "诈骗", "空投"]):
        await update.message.reply_text("⚠️ Reminder: Never click on unofficial airdrop links.")
        return

    if any(x in msg for x in ["ca", "合約", "contract", "價格", "價錢", "price"]):
        price, market_cap = get_e3a_price()
        if price:
            await update.message.reply_text(
                f"📊 *E3A Token Info:*\n\n🔗 Contract: `{E3A_ADDRESS}`\n💰 Price: ${price}\n📈 Market Cap: ${market_cap:,} USD",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("Failed to fetch price data.")
        return

    links_map = {
        "官網": "https://ai.eternalai.io/",
        "eternalai": "https://ai.eternalai.io/",
        "白皮書": "https://ai.eternalai.io/static/Helloworld.pdf",
        "discord": "https://discord.com/invite/ZM7EdkCHZP",
        "telegram": "https://t.me/AIHelloWorld",
        "twitter": "https://x.com/e3a_eternalai?s=21&t=nKJh8aBy_Qblb-XTWP-UpQ"
    }

    for keyword, link in links_map.items():
        if keyword in msg:
            await update.message.reply_text(link)
            return

    emotion_reply = await emotion_response(msg)
    if emotion_reply:
        await update.message.reply_text(emotion_reply)
        return


# === 主程式 ===
def main():
    print("🚀 Bot 正在啟動中...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.bot.delete_webhook(drop_pending_updates=True)

    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("faq", faq))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(lambda ctx: asyncio.create_task(tweet_watcher(app)), interval=300, first=1)

    print("📡 Bot 已啟動，開始 polling 中...")
    app.run_polling()


if __name__ == '__main__':
    main()
