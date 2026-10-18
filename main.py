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

# ১. রেন্ডারের পোর্ট ওপেন রাখার জন্য একটি মিনি ওয়েব সার্ভার (থ্রেডে চলবে)
def run_dummy_server():
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Dummy web server running on port {PORT}")
        httpd.serve_forever()

# ২. ট্র্যাকিং ফাংশন
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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
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
            
            page_text = soup.get_text(separator='\n')
            lines = [line.strip() for line in page_text.splitlines() if line.strip()]
            clean_text = '\n'.join(lines)

            if len(clean_text) > 3800:
                clean_text = clean_text[:3800] + "\n\n...[বাকি অংশ কাটা হয়েছে]"

            if len(clean_text) < 30:
                await update.message.reply_text("ওয়েবসাইট থেকে কোনো তথ্য পাওয়া যায়নি।")
            else:
                await update.message.reply_text(f"📄 **ওয়েবসাইট থেকে পাওয়া রেসপন্স:**\n\n{clean_text}")
        else:
            await update.message.reply_text(f"সার্ভার সাড়া দিচ্ছে না। Error Status Code: {response.status_code}")

    except Exception as e:
        await update.message.reply_text(f"এরর দেখা দিয়েছে: {str(e)}")

def main():
    if not TOKEN:
        print("Error: Telegram Bot Token is missing!")
        return

    # মিনি ওয়েব সার্ভার আলাদা থ্রেডে চালু করা (যাতে রেন্ডার পোর্ট ওপেন পায়)
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    # টেলিগ্রাম বট স্টার্ট করা
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), track_parcel))

    print("বট চালুর জন্য প্রস্তুত...")
    application.run_polling()

if __name__ == '__main__':
    main()
