import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = os.environ.get('TOKEN')

async def track_parcel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cn_number = update.message.text.strip()
    
    if not cn_number.isdigit():
        await update.message.reply_text("দয়া করে সঠিক সুন্দরবন কুরিয়ারের ট্র্যাকিং (CN) নম্বর দিন।")
        return

    await update.message.reply_text(f"🔍 ট্র্যাকিং নম্বর `{cn_number}` এর তথ্য খোঁজা হচ্ছে...")

    try:
        # সুন্দরবন কুরিয়ার সার্ভিসের ট্র্যাকিং ইউআরএল
        url = "https://sundarbancourierltd.com/cntrack.php" # অথবা আপনার আগের ইউআরএল

        # ব্রাউজারের মতো অভিনয় করার জন্য হেডার
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://sundarbancourierltd.com/'
        }

        # ফর্ম সাবমিশনের ডেটা
        data = {
            'cn': cn_number,
            'search': 'Search'
        }

        # POST এবং GET দুটোই চেষ্টা করবে
        response = requests.post(url, data=data, headers=headers, timeout=15)
        
        if response.status_code != 200:
            # যদি POST না কাজ করে তবে GET দিয়ে ট্রাই করবে
            response = requests.get(f"https://sundarbancourierltd.com/track?cn={cn_number}", headers=headers, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # পুরো HTML পেজ থেকে পরিষ্কার টেক্সট বের করা
            page_text = soup.get_text(separator='\n')
            
            # অপ্রয়োজনীয় খালি স্পেস ও লাইন মুছে ফেলা
            lines = [line.strip() for line in page_text.splitlines() if line.strip()]
            clean_text = '\n'.join(lines)

            # মেসেজ সাইজ ৪০০০ ক্যারেক্টারের বেশি হলে কেটে ছোট করা
            if len(clean_text) > 4000:
                clean_text = clean_text[:4000] + "\n\n...[বাকি অংশ কাটা হয়েছে]"

            if len(clean_text) < 20:
                await update.message.reply_text("পেজে কোনো তথ্য পাওয়া যায়নি বা পেজ খালি।")
            else:
                await update.message.reply_text(f"📄 **ওয়েবসাইট থেকে পাওয়া সরাসরি টেক্সট:**\n\n{clean_text}")
        else:
            await update.message.reply_text(f"ওয়েবসাইট সাড়া দিচ্ছে না। Status Code: {response.status_code}")

    except Exception as e:
        await update.message.reply_text(f"এরর দেখা দিয়েছে: {str(e)}")

def main():
    if not TOKEN:
        print("Error: Telegram Bot Token is missing!")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), track_parcel))

    print("বট চালুর জন্য প্রস্তুত...")
    application.run_polling()

if __name__ == '__main__':
    main()
