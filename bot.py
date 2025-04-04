import os
import random
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# === 載入環境變數 ===
load_dotenv()

TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
E3A_ADDRESS = 'EKYotMbZR82JAVakfnaQbRfCE7oyWLsXVwfyjwTRdaos'

# === 回應詞庫 ===
text_responses = {
    "gm": [
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
# === 截圖 ===
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

# === 指令處理 ===
def get_price(update: Update, context):
    price, market_cap = get_e3a_price()
    if price:
        update.message.reply_text(f"🌕 E3A 合約地址：\n{E3A_ADDRESS}\nE3A 現價：${price}\n市值：${market_cap:,} USD")
    else:
        update.message.reply_text("無法取得 E3A 價格資訊。")

# === 一般訊息回覆 ===
def handle_message(update: Update, context):
    msg = update.message.text.lower()

    if any(x in msg for x in ["ca", "合約", "contract"]):
        price, market_cap = get_e3a_price()
        if price:
            update.message.reply_text(
                f"📊 *E3A Token Info*\n\n🔗 Contract: `{E3A_ADDRESS}`\n💰 Price: ${price}\n📈 Market Cap: ${market_cap:,} USD",
                parse_mode='Markdown'
            )
            chart = screenshot_chart()
            if chart:
                with open(chart, 'rb') as photo:
                    update.message.reply_photo(photo=photo)
        else:
            update.message.reply_text("Failed to fetch price data.")
        return



    if any(x in msg for x in ["價格", "價錢", "price"]):
        return get_price(update, context)

    if any(k in msg for k in ["官網", "eternalai", "網站", "site", "網址"]):
        return update.message.reply_text("https://ai.eternalai.io/")
    if any(k in msg for k in ["白皮書", "paper", "whitepaper"]):
        return update.message.reply_text("https://ai.eternalai.io/static/Helloword.pdf")
    if any(k in msg for k in ["discord", "dc"]):
        return update.message.reply_text("https://discord.com/invite/ZM7EdkCHZP")
    if any(k in msg for k in ["telegram", "電報", "社群"]):
        return update.message.reply_text("https://t.me/AIHelloWorld")
    if any(k in msg for k in ["twitter", "推特"]):
        return update.message.reply_text("https://x.com/e3a_eternalai?s=21&t=nKJh8aBy_Qblb-XTWP-UpQ")

    for keyword, replies in text_responses.items():
        if keyword in msg:
            return update.message.reply_text(random.choice(replies))


# === 主程式 ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("price", get_price))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("📡 Bot 正在 Render 上瘋狂跑起來（希望）...")
    app.run_polling()

if __name__ == "__main__":
    main()
