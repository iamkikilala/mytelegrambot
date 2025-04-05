import os
import random
import requests
import feedparser
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# === 載入環境變數 ===
load_dotenv()

TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
E3A_ADDRESS = 'EKYotMbZR82JAVakfnaQbRfCE7oyWLsXVwfyjwTRdaos'
CHAT_ID = os.environ.get("CHAT_ID", "-100xxxxxxxxxx")  # 替換為你的群組 chat_id
text_responses = {
    "gm": [
        "GM~ your message just turned on my happy mode! 🧡",
        "GM! Ready to slay the day 🚀",
        "GM~ don’t forget to smile today 😊",
        "GM~ let’s stay supercharged today ⚡️",
        "Good morning… booting brain… loading… please wait… 😅",
        "I’m up. Time to conquer the world. 🌎",
        "Wishing you a day wrapped in sunshine and smiles 😻",
        "Rise n' shine, web3 warrior! ☀️",
        "Good mooooorning, code monkey 🐵",
        "Wake up, sleepy blockchain hero! 🛌",
        "Your gm unlocked 3 serotonin points ☕",
        "Morning bytes received successfully 💾",
        "You survived the night again. Congrats. 🧟",
        "New day, same chaos. Let’s go! 💥",
        "Here’s your GM. Use it wisely. 🧠"
    ],
    "gn": [
        "GN~ the moon’s on babysitting duty tonight 🌚",
        "Rest well, tomorrow’s you is gonna glow brighter 🙌",
        "GN~ you did great today, proud of you 😌",
        "GN~ hope life didn’t hit too hard today 🩵",
        "Eyes shutting down… brain offline… see ya in dreamland… 😴",
        "Dream sweet, don’t let the bugs bite 🐛",
        "GN lil crypto potato 🥔💤",
        "Sleep mode: ON. Responsiveness: 0% 💤",
        "Nighty night, gas fees are lower anyway 🌌",
        "Time to recharge your mental battery 🔋",
        "Offline until further notice. Goodnight ✨",
        "Shut down sequence initiated... GN 🌙",
        "Logging off from reality 🛏️",
        "Sending you sweet dreams on-chain 🌠",
        "Tomorrow is another coin flip 🪙"
    ],
    "早安": [
        "早啊！新的一天開始囉 🌞",
        "早安～今天也要閃閃發光 ✨",
        "早安你好～願你今天順順利利 🐣",
        "嘿！早上好，元氣滿滿地出發吧 💪",
        "別忘了打卡發光哦 ✨",
        "今天的天氣：適合賺錢 ☀️",
        "咖啡已就位，你呢？ ☕",
        "打開眼睛就是勝利的一天 ✨",
        "你醒了？世界好像開始動了 🌀",
        "祝你早上可愛，下午厲害 💃"
        "新的一天，新的 bug！🤦",
        "你比太陽還早起，了不起！🥳",
        "連夢都捨不得你醒，太可愛啦 😚",
        "早晨就像你的臉一樣明亮（？）🌞",
        "打開窗，吸一口元氣空氣！🌿",
        "今天有你就很閃亮！💫",
        "早安！今天是勇敢小天使日！🪖",
        "來～早安魔法傳送給你 ✨",
        "別讓鬧鐘白叫了，起床發光！🚗",
        "打卡人生，從早安開始！💼"
    ],
    "晚安": [
        "蓋好棉被，作個美夢 🛌",
        "晚安囉～辛苦一天了 ✨",
        "晚安晚安～記得放鬆 🌙",
        "洗洗睡吧，明天會更好 🌟",
        "放下手機，你值得好眠 📴",
        "今晚就讓靈魂放個假吧 💤",
        "夢裡也要記得笑 😊",
        "明天再繼續發光 ✨",
        "你今天超棒，晚安勇者 💪",
        "世界太吵，夢裡我們自己決定 🎧",
        "夜深了，快去當夢境的主角 🛌",
        "刷牙+棉被=超級傳送門 🛎️",
        "今晚的星星為你閃閃發光 ✨",
        "願你夢見100倍幣 🪙",
        "今天的你，值得五星級好夢 ⭐",
        "放空 + 發呆 + zzz 模式啟動 🧦",
        "夢裡我會繼續陪你吐槽人生 🤪",
        "讓疲憊像殭屍一樣爛掉吧 🦜",
        "晚安～記得對自己說聲辛苦了！🤍",
        "睡眠任務已接收，準備執行！😷"
],
     "早上好": [  
         "早上好哇！今天會發光 ✨",
         "一起元氣出發吧！ 🚗",
         "你是今天的限量閃亮星 🌟",
         "打開眼睛，收下宇宙的祝福 🌼",
         "喂～你是不是還在床上？快醒醒！😭",
         "陽光曬屁股啦！🌞",
         "早上好，今天準備登場了嗎？ 🌈",
         "起床就像開機一樣，現在 boot 完了嗎？🚄",
         "比鬧鐘還早醒的你，超猛 🚫☕",
         "早上好啊！請收下這顆元氣彈 💥",
         "今天的你：可愛100%、困意80% 😪",
         "早上好，請保持可愛直到晚上 😍",
         "太陽公公都在找你了 🌞",
         "早餐加你就滿分了！🥞",
         "醒了就不許再賴床喔 🥴",
         "今天要勇敢，也要可愛 😺",
         "祝你今天沒有bug只有糖果 🍬",
         "笑一個，才有好運出門喔！🙌",
         "你的訊息是我今天的陽光 ☀️",
         "打起精神，今天也要超厲害！💪"
],
"晚上好": [
        "晚上好！記得放鬆一下吧 🌚",
        "嘿～你又撐過一天啦！🚀",
        "來點晚安魔法嗎？✨🌟",
        "今晚的空氣有點夢幻唷 🌌",
        "晚上好呀，準備變成沙發馬鈴薯了嗎？🥔",
        "這時段最適合看星星和耍廢 🛌",
        "祝你有個閃亮又舒服的夜晚 🌃",
        "今晚別熬夜唷（雖然我知道你會） 😭",
        "給今天的你一顆溫暖的晚安糖 🍬",
        "夜色迷人，但你更閃亮 😉",
        "卸下疲憊，準備飛進夢裡啦 🌠",
        "你今天真的有夠棒，給你拍拍手 👏",
        "晚上好～先來一口宵夜開局 🥜",
        "希望你夢到的幣都暴漲 🚀",
        "月亮在偷看你打開 Telegram 🌜",
        "夜深了，記得多抱抱自己 🤍",
        "給你一張入夢的 VIP 入場券 🎈",
        "準備進入放空模式...啟動！ 🛏️",
        "晚風剛剛好，剛好可以當藉口耍廢 🍃",
        "你已經夠努力了，來點放鬆吧 🌙"
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

# === /faq 指令 ===
async def faq(update: Update, context):
    text = """❓ *FAQ:*\n
*Q:* Where to buy E3A?
*A:* You can view it on [DexScreener](https://dexscreener.com/).

*Q:* Total Supply?
*A:* 1,000,000,000

*Q:* Will it be listed on CEX?
*A:* Yes, roadmap includes Tier 1 exchange goals.
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# === /stats 指令 ===
async def stats(update: Update, context):
    price, market_cap = get_e3a_price()
    if price:
        await update.message.reply_text(
            f"📊 *E3A Token Stats:*\n\n"
            f"Price: ${price}\n"
            f"Market Cap: ${market_cap:,} USD\n"
            f"Contract: {E3A_ADDRESS}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Failed to fetch stats.")
# === 處理文字訊息 ===
async def handle_message(update: Update, context):
    msg = update.message.text.lower()
    print(f"收到訊息：{msg}")

    # scam 偵測
    if any(word in msg for word in ["airdrop", "fakewallet", "詐騙", "空投"]):
        await update.message.reply_text(
            "⚠️ Reminder: Never click on unofficial airdrop links. Always verify with the team."
        )
        return

    # 合約或價格關鍵詞查詢
    if any(x in msg for x in ["ca", "合約", "contract", "價格", "價錢", "price"]):
        price, market_cap = get_e3a_price()
        if price:
            await update.message.reply_text(
                f"📊 *E3A Token Info*\n\n"
                f"🔗 Contract: `{E3A_ADDRESS}`\n"
                f"💰 Price: ${price}\n"
                f"📈 Market Cap: ${market_cap:,} USD",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("Failed to fetch price data.")
        return

    # 常用資訊
    if any(k in msg for k in ["官網", "eternalai", "網站", "site", "網址"]):
        await update.message.reply_text("https://ai.eternalai.io/")
        return
    if any(k in msg for k in ["白皮書", "paper", "whitepaper"]):
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

    # 關鍵字對應的詞庫
    for keyword, replies in text_responses.items():
        if keyword in msg:
            await update.message.reply_text(random.choice(replies))
            return

# === 啟動主程式 ===
def main():
    print("🚀 Bot 正在啟動中...")
    application = ApplicationBuilder().token(TOKEN).build()
    application.bot.delete_webhook(drop_pending_updates=True)

    # 指令
    application.add_handler(CommandHandler("price", get_price))
    application.add_handler(CommandHandler("faq", faq))
    application.add_handler(CommandHandler("stats", stats))

    # 文字訊息與 scam 偵測
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Entity("url"), scam_link_checker))

    # 啟動 Tweet Watcher
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_once(
            lambda ctx: asyncio.create_task(tweet_watcher(application)),
            when=1
        )
    else:
        print("⚠️ JobQueue 尚未啟用，無法設置 tweet_watcher 任務。")

    print("📡 Bot 已啟動，開始 polling 中...")
    application.run_polling()

