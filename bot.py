import os
import random
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === 載入 .env 檔（請確保 .env 已加入 .gitignore） ===
load_dotenv()

# 從環境變數讀取必要資訊
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://your-app-name.onrender.com")
PORT = int(os.environ.get("PORT", 8080))
CHAT_ID = os.environ.get("CHAT_ID", "-1002606282067")  # 如有需要可用

# E3A 合約地址（固定值）
E3A_ADDRESS = 'EKYotMbZR82JAVakfnaQbRfCE7oyWLsXVwfyjwTRdaos'

# === 回應詞庫（英文版） ===
text_responses = {
    "gm": [
        "Morning sunshine! Let’s sparkle today 🌞",
        "GM~ your message just turned on my happy mode! 🧡",
        "GM! Ready to slay the day 🚀",
        "GM~ don’t forget to smile today 😊",
        "GM~ let’s stay supercharged today ⚡️",
        "Good morning… booting brain… loading… please wait… 😅",
        "I’m up. Time to conquer the world. 🌎",
        "Wishing you a day wrapped in sunshine and smiles 😻"
    ],
    "gn": [
        "GN~ the moon’s on babysitting duty tonight 🌚",
        "Rest well, tomorrow’s you is gonna glow brighter 🙌",
        "GN~ you did great today, proud of you 😌",
        "GN~ hope life didn’t hit too hard today 🩵",
        "Eyes shutting down… brain offline… see ya in dreamland… 😴"
    ],
    "good morning": [
        "Good morning! A new day has begun 🌞",
        "Good morning! Shine on and have a great day ✨",
        "Morning! Hope your day is filled with success 🐣",
        "Hey, good morning! Let's start the day full of energy 💪"
    ],
    "good night": [
        "Good night! Sweet dreams 🛌",
        "Good night, hope you rest well ✨",
        "Good night! Relax and recharge 🌙",
        "Sleep tight and see you tomorrow 🌟"
    ],
    "早安": [
        "早啊！新的一天開始囉 🌞",
        "早安～今天也要閃閃發光 ✨",
        "早安你好～願你今天順順利利 🐣",
        "嘿！早上好，元氣滿滿地出發吧 💪"
    ],
      "早上好": [
      "嗨～早上好呀！☀️",
      "今天也是充滿希望的一天 ✨",
      "早上好！新的一天冒險開始 🎒",
       "祝你今天好運連連 🍀"
    ],
     "晚安": [
     "蓋好棉被，作個美夢 🛌",
     "晚安囉～辛苦一天了 ✨",
     "晚安晚安～記得放鬆 🌙",
     "洗洗睡吧，明天會更好 🌟"
      ]
}


# === DexScreener 查詢價格 ===
def get_e3a_price():
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={E3A_ADDRESS}"
        res = requests.get(url)
        data = res.json()
        pair = data.get('pairs', [{}])[0]
        price = pair.get('priceUsd')
        market_cap = pair.get('marketCap')
        if price and market_cap:
            return price, market_cap
        else:
            return None, None
    except Exception as e:
        print("Price fetch error:", e)
        return None, None

# === 產生價格走勢圖（利用 Selenium 截圖 Dexscreener 網頁） ===
def screenshot_chart():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # 此處以 Solana 為例，如有需要請依合約平台調整 URL
        url = f"https://dexscreener.com/solana/{E3A_ADDRESS}"
        driver.set_window_size(1280, 720)
        driver.get(url)
        driver.implicitly_wait(5)

        screenshot_path = "chart.png"
        driver.save_screenshot(screenshot_path)
        driver.quit()
        return screenshot_path
    except Exception as e:
        print("Screenshot error:", e)
        return None

# === /price 指令（僅回覆文字價格資訊） ===
async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price, market_cap = get_e3a_price()
    if price:
        await update.message.reply_text(
            f"🌕 E3A Contract Address:\n{E3A_ADDRESS}\n"
            f"Current Price: ${price}\nCirculating Market Cap: ${market_cap:,} USD"
        )
    else:
        await update.message.reply_text("Unable to retrieve E3A price information.")

# === 歡迎新用戶（英文歡迎） ===
async def welcome_on_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            name = member.first_name
            greetings = [
                f"🎉 Welcome aboard, {name}!",
                f"🤖 {name} just joined the AI side!",
                f"✨ {name}, glad you made it. Sit down, grab a snack.",
                f"Hey {name}! You're now one of us. 😎"
            ]
            await update.message.reply_text(random.choice(greetings))

# === 文字訊息處理（依關鍵字進行不同回覆） ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()

    # 合約查詢（包含 "ca", "contract", "contract address", "合約"）
    if any(x in msg for x in ["ca", "contract", "contract address", "合約"]):
        price, market_cap = get_e3a_price()
        if price:
            await update.message.reply_text(
                f"🌕 E3A Contract Address:\n{E3A_ADDRESS}\n"
                f"Current Price: ${price}\nCirculating Market Cap: ${market_cap:,} USD"
            )
            # 產生價格走勢圖（使用非同步方式執行避免阻塞）
            image_path = await asyncio.to_thread(screenshot_chart)
            if image_path:
                with open(image_path, 'rb') as photo:
                    await update.message.reply_photo(photo=photo)
        else:
            await update.message.reply_text("Unable to retrieve E3A price information.")
        return

    # 價格查詢（包含 "price", "cost", "價格", "價錢"）
    if any(k in msg for k in ["price", "cost", "價格", "價錢"]):
        await get_price(update, context)
        return

    # 網站與資源查詢（中英混合）
    if any(k in msg for k in ["website", "官網", "site", "eternalai", "網址"]):
        await update.message.reply_text("[EternalAI](https://ai.eternalai.io/)", parse_mode='Markdown')
        return
    if any(k in msg for k in ["whitepaper", "paper", "白皮書"]):
        await update.message.reply_text("https://ai.eternalai.io/static/Helloword.pdf")
        return
    if any(k in msg for k in ["discord", "dc"]):
        await update.message.reply_text("https://discord.com/invite/ZM7EdkCHZP")
        return
    if any(k in msg for k in ["telegram", "電報", "社群"]):
        await update.message.reply_text("https://t.me/AIHelloWorld")
        return
    if any(k in msg for k in ["twitter", "推特"]):
        await update.message.reply_text("https://x.com/e3a_eternalai?s=21&t=nKJh8aBy_Qblb-XTWP-UpQ")
        return

    # 其他自動回覆（以英文回覆）
    for keyword, replies in text_responses.items():
        if keyword in msg:
            await update.message.reply_text(random.choice(replies))
            return

# === 啟動主程式（採用 Webhook 模式，適合雲端部屬）===
import asyncio
import os

async def main():
    app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()

    app.add_handler(CommandHandler("price", get_price))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_on_join))

    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        webhook_url=f"{os.environ.get('WEBHOOK_URL')}/"
    )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
git commit -m "fix: avoid RuntimeError - event loop already running"
git push
