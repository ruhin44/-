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

    await update.message.reply_text(f"🔍 ট্র্যাকিং নম্বর `{cn_number}` এর তথ্য খোঁজা হচ্ছে...")

    try:
        api_url = "https://operation.sundarbancourierltd.com/Home/getDatabyCN"

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

        payload = {
            "selectedtypes": "cnno",
            "selectedtimes": "7",
            "inputvalue": cn_number
        }

        response = requests.post(api_url, json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            res_data = response.json()
            
            if res_data and isinstance(res_data, list) and len(res_data) > 0:
                item = res_data[0]
                
                cn = item.get('cnNumber', cn_number)
                status = item.get('status', 'N/A')
                item_desc = item.get('itemDescription', 'N/A')
                booking_from = item.get('bookingBranch', 'N/A')
                destination = item.get('destBranch', 'N/A')
                booking_date = item.get('bookingDate', '').split('T')[0] if item.get('bookingDate') else 'N/A'
                
                # সুন্দরভাবে সাজানো মেসেজ ফরম্যাট
                msg = f"📦 **সুন্দরবন কুরিয়ার ট্র্যাকিং রিপোর্ট**\n\n"
                msg += f"🔹 **CN Number:** `{cn}`\n"
                msg += f"🛍️ **আইটেম:** {item_desc}\n"
                msg += f"🚩 **বুকিং শাখা:** {booking_from}\n"
                msg += f"🏁 **গন্তব্য শাখা:** {destination}\n"
                msg += f"📅 **বুকিং তারিখ:** {booking_date}\n"
                msg += f"📌 **বর্তমান স্ট্যাটাস:** `{status}`\n\n"
                msg += f"📜 **ট্র্যাকিং হিস্ট্রি:**\n"
                
                status_list = item.get('cnStatusList', [])
                for s in status_list:
                    s_date = s.get('statusDate', '')
                    s_date_str = s_date.split('T')[0] if s_date else ''
                    s_status = s.get('status', '')
                    sub_branch = s.get('fromSubBranch', '') or s.get('downloadSubBranchName', '')
                    remarks = s.get('remarks', '')
                    
                    msg += f"• `{s_date_str}` — **{s_status}**"
                    if sub_branch:
                        msg += f" ({sub_branch})"
                    if remarks:
                        msg += f" [{remarks}]"
                    msg += "\n"

                # টেলিগ্রামের মেসেজ লিমিট (৪০০০ ক্যারেক্টার) চেক করা
                if len(msg) > 4000:
                    msg = msg[:3950] + "\n\n...(টেক্সট বড় হওয়ায় কিছু অংশ বাদ দেওয়া হয়েছে)"

                await update.message.reply_text(msg, parse_mode='Markdown')
            else:
                await update.message.reply_text("দুঃখিত, এই ট্র্যাকিং নম্বরের বিপরীতে কোনো ডাটা পাওয়া যায়নি। সঠিক নম্বর দিয়েছেন কি না চেক করুন।")
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
