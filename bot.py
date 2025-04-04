import os
import random
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# === 載入 .env 檔 ===
load_dotenv()

# 環境變數
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID = os.environ.get("CHAT_ID", "-1002606282067")
E3A_ADDRESS = 'EKYotMbZR82JAVakfnaQbRfCE7oyWLsXVwfyjwTRdaos'

# === 回應詞庫（中英混合） ===
text_responses = {
    "gm": [
        "GM~ your message just turned on my happy mode! 🦡",
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
        "Eyes shutting down… brain offline… see ya in dreamland… 🛌"
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
    except Exception as e:
        print("幣價錯誤：", e)
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

# === /price 指令 ===
async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price, market_cap = get_e3a_price()
    if price:
        await update.message.reply_text(
            f"🌕 E3A 合約地址：\n{E3A_ADDRESS}\nE3A price：${price}\nmarket cap：${market_cap:,} USD"
        )
        chart = screenshot_chart()
        if chart:
            await update.message.reply_photo(photo=open(chart, 'rb'))
    else:
        await update.message.reply_text("無法取得 E3A 價格資訊。")

# === 歡迎新用戶 ===
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

# === 文字訊息處理 ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()

    if any(x in msg for x in ["ca", "合約", "contract"]):
        price, market_cap = get_e3a_price()
        if price:
            await update.message.reply_text(
                f"🌕 E3A 合約地址：\n{E3A_ADDRESS}\nE3A 現價：${price}\n流通市值：${market_cap:,} USD")
        else:
            await update.message.reply_text("無法取得幣價資訊")
        return

    if any(k in msg for k in ["價格", "價錢", "price"]):
        await get_price(update, context)
        return

    if any(k in msg for k in ["官網", "网站", "網站", "site", "eternalai", "網址"]):
        await update.message.reply_text("[EternalAI](https://ai.eternalai.io/)", parse_mode='Markdown')
        return
    if any(k in msg for k in ["白皮書", "whitepaper", "paper"]):
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

    for keyword, replies in text_responses.items():
        if keyword in msg:
            await update.message.reply_text(random.choice(replies))
            return

# === 主程式 ===
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("price", get_price))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_on_join))

    await app.run_polling()  # 改成輪詢模式

# === 避免事件迴圈衝突 ===
if __name__ == '__main__':
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(main())
