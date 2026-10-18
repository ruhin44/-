import os
import http.server
import socketserver
import threading
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = os.environ.get('TOKEN')
PORT = int(os.environ.get('PORT', 10000))

def run_dummy_server():
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

async def track_parcel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cn_number = update.message.text.strip()
    
    if not cn_number.isdigit():
        await update.message.reply_text("দয়া করে সঠিক সুন্দরবন কুরিয়ারের ট্র্যাকিং (CN) নম্বর দিন।")
        return

    await update.message.reply_text(f"🔍 ট্র্যাকিং নম্বর `{cn_number}` এর তথ্য খোঁজা হচ্ছে...")

    try:
        url = "https://operation.sundarbancourierltd.com/"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://operation.sundarbancourierltd.com/'
        }

        payload = {
            'search_type': 'CN Number',
            'date_range': 'Last 7 days',
            'search_value': cn_number,
            'cn': cn_number
        }

        session = requests.Session()
        session.get(url, headers=headers, timeout=10)
        response = session.post(url, data=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # শুধুমাত্র ওয়েবসাইটের টেবিলগুলো থেকে ডেটা ফিল্টার করা
            tables = soup.find_all('table')
            extracted_data = []

            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    cols_text = [ele.text.strip() for ele in cols if ele.text.strip()]
                    if cols_text:
                        extracted_data.append(" : ".join(cols_text))

            if extracted_data:
                clean_result = "\n".join(extracted_data)
                await update.message.reply_text(f"📦 **পার্সেলের রিয়েল-টাইম আপডেট:**\n\n{clean_result}")
            else:
                await update.message.reply_text("দুঃখিত, এই ট্র্যাকিং নম্বরের কোনো আপডেট পাওয়া যায়নি। সঠিক নম্বর দিয়েছেন কি না চেক করুন।")
        else:
            await update.message.reply_text("সার্ভার থেকে সঠিক ডেটা পাওয়া যায়নি।")

    except Exception as e:
        await update.message.reply_text(f"টেকনিক্যাল সমস্যার কারণে খোঁজ করা সম্ভব হয়নি।")

def main():
    if not TOKEN:
        print("Error: Telegram Bot Token is missing!")
        return

    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), track_parcel))

    print("বট চালুর জন্য প্রস্তুত...")
    application.run_polling()

if __name__ == '__main__':
    main()
