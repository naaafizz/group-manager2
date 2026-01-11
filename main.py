from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# আপনার দেওয়া ডিটেইলস
API_ID = 37621701
API_HASH = "dbc57dc85eff3ec5a1cb44f9d41ab9d9"
BOT_TOKEN = "7998732562:AAGbIuAgHKye5-1dVcp93YaBroLH3qkxpvg"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ডেটাবেস হিসেবে ডিকশনারি (বট রিস্টার্ট দিলে এটি রিসেট হবে)
# স্থায়ী করতে চাইলে পরে MongoDB যোগ করা যাবে
settings = {}

# ইউজার অ্যাডমিন কি না চেক করার ফাংশন
async def is_admin(chat_id, user_id):
    member = await app.get_chat_member(chat_id, user_id)
    return member.status in ("administrator", "creator")

# ১. জয়েন/লিভ মেসেজ অটো ডিলিট
@app.on_message(filters.service)
async def delete_service_msgs(client, message):
    await message.delete()

# ২. অ্যাডমিন লিঙ্ক সেট করার কমান্ড (/setlink https://t.me/example)
@app.on_message(filters.command("setlink") & filters.group)
async def set_link(client, message):
    if await is_admin(message.chat.id, message.from_user.id):
        if len(message.command) > 1:
            new_link = message.command[1]
            settings[message.chat.id] = new_link
            await message.reply_text(f"✅ সাকসেস! নতুন লিঙ্ক সেট হয়েছে:\n`{new_link}`")
        else:
            await message.reply_text("ব্যবহার: `/setlink [আপনার লিঙ্ক]`")
    else:
        await message.reply_text("❌ শুধু অ্যাডমিনরা লিঙ্ক সেট করতে পারবেন।")

# ৩. লিঙ্ক এবং ফরওয়ার্ড ফিল্টার
@app.on_message(filters.group & ~filters.service)
async def filter_all(client, message):
    # অ্যাডমিনদের মেসেজ ফিল্টার হবে না
    if message.from_user and await is_admin(message.chat.id, message.from_user.id):
        return

    # লিঙ্ক থাকলে বা ফরওয়ার্ড হলে
    has_link = filters.url(message) or (message.text and "t.me" in message.text)
    is_forwarded = message.forward_from or message.forward_from_chat

    if has_link or is_forwarded:
        await message.delete()
        
        # বাটন পাঠানো
        target_link = settings.get(message.chat.id, "https://t.me/your_channel")
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 গেট লিঙ্ক / Get Link", url=target_link)]
        ])
        
        await message.reply_text(
            f"नमस्ते {message.from_user.mention},\nএখানে সরাসরি লিঙ্ক বা ফরওয়ার্ড এলাউড নয়। নিচের বাটনে ক্লিক করুন:",
            reply_markup=markup
        )

print("বটটি সফলভাবে চালু হয়েছে! (Pyrogram)")
app.run()