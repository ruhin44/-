import os
import http.server
import socketserver
import threading
import requests
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

    await update.message.reply_text(f"🔍 ট্র্যাকিং নম্বর `{cn_number}` এর রিয়েল-টাইম ডাটা আনা হচ্ছে...")

    try:
        # আপনার খুঁজে বের করা আসল এপিআই লিংক
        api_url = "https://operation.sundarbancourierltd.com/Home/getDatabyCN"

        # আপনার দেওয়া সঠিক হেডার্স এবং কাস্টম কী (Key)
        headers = {
            'Host': 'operation.sundarbancourierltd.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-T595 Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.8037.107 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://operation.sundarbancourierltd.com',
            'X-Requested-With': 'XMLHttpRequest',
            'key': 'CzbZcWnwf7TNTzluD9rxyXCUqzN4xOhs',
            'Referer': 'https://operation.sundarbancourierltd.com/'
        }

        # আপনি যে পেলোড বা বডি বের করেছেন
        payload = {
            "selectedtypes": "cnno",
            "selectedtimes": "7",
            "inputvalue": cn_number
        }

        # সরাসরি JSON এপিআইতে POST রিকোয়েস্ট পাঠানো
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            res_data = response.json()
            
            if res_data:
                # ডেটা সুন্দরভাবে সাজিয়ে পাঠানোর জন্য ফরম্যাট করা
                # (রেসপন্স জেসন ফরম্যাট অনুযায়ী ফিল্ডগুলো সাজানো যাবে)
                text_output = f"📦 **সুন্দরবন কুরিয়ার ট্র্যাকিং রিপোর্ট:**\n\n```json\n{res_data}\n```"
                await update.message.reply_text(text_output, parse_mode='Markdown')
            else:
                await update.message.reply_text("দুঃখিত, এই ট্র্যাকিং নম্বরের বিপরীতে কোনো ডাটা পাওয়া যায়নি।")
        else:
            await update.message.reply_text(f"সার্ভার ত্রুটি কোড: {response.status_code}")

    except Exception as e:
        await update.message.reply_text(f"টেকনিক্যাল সমস্যার কারণে খোঁজ করা সম্ভব হয়নি: {str(e)}")

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
