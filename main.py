
import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# রেন্ডারের এনভায়রনমেন্ট ভেরিয়েবল থেকে বটের টোকেন নেওয়া হবে
TOKEN = os.environ.get('TOKEN')

async def track_parcel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cn_number = update.message.text.strip()
    
    # শুধু নম্বর কি না চেক করা
    if not cn_number.isdigit():
        await update.message.reply_text("দয়া করে সঠিক সুন্দরবন কুরিয়ারের ট্র্যাকিং (CN) নম্বর দিন। যেমন: 1047700039006")
        return

    await update.message.reply_text(f"🔍 ট্র্যাকিং নম্বর `{cn_number}` এর তথ্য খোঁজা হচ্ছে, একটু অপেক্ষা করুন...")

    try:
        # সুন্দরবন কুরিয়ারের ট্র্যাকিং লিংক বা রিকোয়েস্ট সেটআপ
        target_url = f"https://sundarbancourierltd.com/track?cn={cn_number}"
        
        # হেডার্স যুক্ত করা যাতে ওয়েবসাইট ব্লক না করে
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # এখানে স্ক্র্যাপ করার লজিক বসবে। আপাতত সুন্দর একটি ডেমো স্টাইলে আউটপুট দেওয়া হলো:
            reply_text = f"""
📦 **পার্সেলের বর্তমান অবস্থা:**
* **CN Number:** {cn_number}
* **Last Status:** দিলকুশা হাব এ রিসিভ সম্পন্ন হয়েছে
* **Date:** ১৬-Oct-2026

📜 **পূর্বের ইতিহাস:**
- ১৫-Oct-2026: রংপুর পীরগঞ্জ থেকে বুকিং সম্পন্ন হয়েছে।
- ১৫-Oct-2026: পেম্টি রংপুর পীরগঞ্জ থেকে দিলকুশা হাব এর উদ্দেশ্যে ছেড়ে গেছে।
- ১৬-Oct-2026: দিলকুশা হাব এ রিসিভ সম্পন্ন হয়েছে।
            """
            await update.message.reply_text(reply_text, parse_mode='Markdown')
        else:
            await update.message.reply_text("দুঃখিত, সার্ভার থেকে ডেটা পাওয়া যায়নি। পরে আবার চেষ্টা করুন।")

    except Exception as e:
        await update.message.reply_text("টেকনিক্যাল সমস্যার কারণে খোঁজ করা সম্ভব হয়নি।")

def main():
    if not TOKEN:
        print("Error: Telegram Bot Token is missing!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    # ব্যবহারকারী ট্র্যাকিং নম্বর পাঠালে এই ফাংশন কাজ করবে
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), track_parcel))

    print("বট সফলভাবে চালু হয়েছে...")
    application.run_polling()

if __name__ == '__main__':
    main()
