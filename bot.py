# === 1. 載入必要套件 ===
import os
import random
import requests
import feedparser
import asyncio
import re
import zhconv
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# === 載入環境變數 ===
load_dotenv()

TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
E3A_ADDRESS = 'EKYotMbZR82JAVakfnaQbRfCE7oyWLsXVwfyjwTRdaos'
CHAT_ID = os.environ.get("CHAT_ID", "-100xxxxxxxxxx")  # 替換為你的群組 chat_id
HELIUS_KEY = os.environ.get("HELIUS_KEY", "your_helius_api_key")
# === Command descriptions for /help ===
command_descriptions = {
    "faq": "Frequently asked questions and answers",
    "stats": "Show E3A live stats: price, market cap, holders, contract",
    "holders": "Display E3A token holder count",
    "help": "Show this command reference list"
}



# === /help 指令 ===
async def help_command(update: Update, context):
    help_text = """✅ *E3A Bot Command Menu*

Here are the available commands:

"""
    for cmd, desc in command_descriptions.items():
        help_text += f"/{cmd} — {desc}\n"

    help_text += """

🔍 *Trigger Keywords:*
- Auto replies to common phrases like: `"gm"`, `"gn"`, `"早安"`, `"晚安"`, `"價格"`, `"合約"`, `"price"` and more.
- Detects scam words like `"空投"` / `"airdrop"` / `"詐騙"` and gives safety warnings.
- Automatically forwards new tweets from EternalAI Twitter.

Enjoy the bot and don’t forget to DYOR 🧠
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

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
# === 3. 問題關鍵字自動回覆字典 ===
question_responses = {
    "這什麼幣|这什么币": "這是比你努力還堅定的幣。",
    "會漲嗎|会涨吗": "這問題和算命沒兩樣。買了你就信，不買你就沒得信。",
    "還能買嗎|还能买吗": "現在不買，未來你會說『早知道』。現在買，未來你會說『太多了』。",
    "能上幣安嗎|能上币安吗": "幣安在我們的 roadmap 裡，社群熱度你有貢獻嗎？🤨",
    "可以 all in 嗎|可以 all in 吗": "可以。房子給我，戶頭給我，E3A 給你。Deal？",
    "地板價多少|地板价多少": "問地板價前，先問問你心裡的底價在哪。😌",
    "騙人吧|骗人吧": "騙你進群的不是我，是希望。這幣沒保證，只有信仰。⛩️",
    "是詐騙嗎|是诈骗吗": "詐騙不會做網站、不會寫合約、不會回你訊息。我們會。你自己判斷。",
    "能空投嗎|能空投吗": "能，但不是現在。你是要空投還是貢獻？順序不能錯。",
    "什麼時候拉盤|什么时候拉盘": "當你停止問這句話的那一刻起，就開始了。📈",
    "怎麼買|怎么买": "怎麼不去點置頂訊息，還在這邊問？😉",
    "好項目介紹一下|好项目介绍一下": "現在看到的就是。剩下的靠緣分，不靠演算法。",
    "多少倍": "你是算命師還是時間旅人？冷靜點。",
    "這是 meme 幣嗎|这是 meme 币吗": "我們是信仰幣，帶點幽默的認真型。",
    "是不是地板了": "沒有最地板，只有更地板。市場是無情的地心引力。",
    "可以借錢買嗎|可以借钱买吗": "可以。但我建議你先借理智回來。",
    "這個項目活著嗎|这个项目活着吗": "你在這個群裡，它還活著。不然我在這幹嘛？",
    "請問 admin 在嗎|请问 admin 在吗": "Admin 不是客服，是生物。他在，他累，他正在 debug。",
    "這群活人嗎|这群活人吗": "你現在講話了，至少有一個是。感謝你冒泡。",
    "可以幫我解釋嗎|可以帮我解释吗": "可以。但你先去看白皮書，我再幫你畫圖。",
    "還會跌嗎|还会跌吗": "會。因為你剛問完。市場就是這麼情緒化。",
    "誰賣的|谁卖的": "不是你就好，別管那麼多。🫣",
    "還有機會嗎|还有机会吗": "機會永遠在，問題是你還在不在。",
    "還沒起飛|还没起飞": "我們這不是火箭，是鯨魚，要慢慢浮出來。🐋",
    "我要多少錢才能財富自由|我要多少钱才能财富自由": "這問題要問財務顧問，不是 telegram bot。😑",
    "能幫我看一下 chart 嗎|能帮我看一下 chart 吗": "圖表給了你方向，信仰給了你勇氣。請自己打開 Dexscreener。",
    "有沒有人回答我|有没有人回答我": "現在有了。你開心了嗎？🥹",
    "可以發在這裡嗎|可以发在这里吗": "如果你不是詐騙，那應該可以。",
    "合約是不是改過|合约是不是改过": "你以為我們是 rug factory？開源透明，不要懷疑人生。",
    "怎麼那麼慢|怎么那么慢": "鏈在動，人心不穩。你以為按下去就發財？先深呼吸。",
    "E3A 是什麼|E3A 是什么": "E3A 是區塊鏈上的 AI 靈魂伴侶，也是你未來的幣圈奇蹟。"
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
# === 5. 查持幣人數功能 ===
def get_holder_count():
    try:
        headers = {"accept": "application/json"}
        url = f"https://api.helius.xyz/v0/token-metadata?api-key={HELIUS_KEY}&mint={E3A_ADDRESS}"
        res = requests.get(url, headers=headers)
        data = res.json()
        return data.get("holders", "N/A")
    except Exception as e:
        print("取得持幣人數失敗：", e)
        return "N/A"

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
*A:* You can buy it here: [DexScreener](https://dexscreener.com/solana/EKYotMbZR82JAVakfnaQbRfCE7oyWLsXVwfyjwTRdaos)\n
*Q:* Total Supply?  
*A:* 1,000,000,000\n
*Q:* Will it be listed on CEX?  
*A:* Yes, roadmap includes Tier 1 exchange goals.
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# === 8. 持幣人數查詢 ===
async def holders(update: Update, context):
    holders = get_holder_count()
    await update.message.reply_text(
        f"📦 Current Holders of E3A: {holders} addresses"
    )


# === /stats 指令 ===
async def stats(update: Update, context):
    price, market_cap = get_e3a_price()
    holders = get_holder_count()
    if price:
        await update.message.reply_text(
            f"📊 *E3A Token Stats:*\n\n"
            f"💰 Price: ${price}\n"
            f"📈 Market Cap: ${market_cap:,} USD\n"
            f"👛 Holders: {holders} addresses\n"
            f"🔗 Contract: `{E3A_ADDRESS}`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Failed to fetch stats.")

# === 10. 處理訊息 ===
import re
import zhconv  # 放最上面 imports 一起

# === 處理訊息 ===
async def handle_message(update: Update, context):
    print("🧠 handle_message 被觸發")
    msg = update.message.text.lower()

    # === scam 偵測 ===
    if any(word in msg for word in ["airdrop", "fakewallet", "詐騙", "诈骗", "空投"]):
        await update.message.reply_text("⚠️ Reminder: Never click on unofficial airdrop links. Always verify with the team.")
        return

    # === 價格與合約關鍵字 ===
    if any(x in msg for x in ["ca", "合約", "contract", "價格", "價錢", "price"]):
        price, market_cap = get_e3a_price()
        if price:
            await update.message.reply_text(
                f"📊 *E3A Token Info:*\n\n"
                f"🔗 Contract: `{E3A_ADDRESS}`\n"
                f"💰 Price: ${price}\n"
                f"📈 Market Cap: ${market_cap:,} USD",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("Failed to fetch price data.")
        return

    # === 官網與常見連結 ===
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

    # === 問題關鍵字自動回覆（簡體轉換＋正則）===
    msg_simplified = zhconv.convert(msg, 'zh-hans')
    for keyword, reply in question_responses.items():
        if re.search(keyword, msg_simplified):
            await update.message.reply_text(reply)
            return

    # === 早安晚安等關鍵詞詞庫 ===
    for keyword, replies in text_responses.items():
        if keyword in msg:
            await update.message.reply_text(random.choice(replies))
            return


# === 11. 主程式 ===
def main():
    print("🚀 Bot 正在啟動中...")
    application = ApplicationBuilder().token(TOKEN).build()
    application.bot.delete_webhook(drop_pending_updates=True)

    application.add_handler(CommandHandler("faq", faq))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("holders", holders))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

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

if __name__ == "__main__":
    main()
