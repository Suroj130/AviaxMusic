import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from AviaxMusic import app
from telegraph import upload_file
import time

# ------------------------------------------------------------------------------- #

@app.on_message(filters.command(["tgm", "tgt", "telegraph", "tl"]))
async def get_telegraph_link(client, message):
    """
    Telegraph এ মিডিয়া আপলোড করার কমান্ড
    """
    if not message.reply_to_message:
        return await message.reply_text(
            "❌ **প্লিজ একটা মিডিয়া ফাইল রিপ্লাই দিন**\n\n"
            "যেমন: ফটো, ভিডিও, ডকুমেন্ট রিপ্লাই করে /tgm লিখুন।"
        )

    media = message.reply_to_message
    file_size = 0
    
    # ফাইলের সাইজ চেক করা
    if media.photo:
        file_size = media.photo.file_size
    elif media.video:
        file_size = media.video.file_size
    elif media.document:
        file_size = media.document.file_size
    elif media.animation:
        file_size = media.animation.file_size
    elif media.audio:
        file_size = media.audio.file_size
    else:
        return await message.reply_text("❌ **শুধু মিডিয়া ফাইল সাপোর্ট করে** (ফটো/ভিডিও/ডকুমেন্ট)")

    # 200MB এর বেশি ফাইল নেয়া যাবে না
    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("❌ **ফাইল সাইজ ২০০MB এর বেশি হতে পারবে না**")

    try:
        # প্রসেসিং মেসেজ
        text = await message.reply_text("⏳ **প্রসেসিং...**")

        # প্রোগ্রেস বার ফাংশন
        async def progress(current, total):
            try:
                percent = current * 100 / total
                await text.edit_text(f"📥 **ডাউনলোডিং...** `{percent:.1f}%`")
            except:
                pass

        # ফাইল ডাউনলোড করা
        local_path = await media.download(progress=progress)
        await text.edit_text("📤 **আপলোডিং টু টেলিগ্রাফ...**")

        # টেলিগ্রাফে আপলোড
        try:
            response = upload_file(local_path)
            upload_url = "https://telegra.ph" + response[0]
        except Exception as e:
            await text.edit_text(f"❌ **আপলোড ব্যর্থ**\n\n**রিজন:** `{str(e)}`")
            os.remove(local_path)
            return

        # সাকসেস মেসেজ
        await text.edit_text(
            f"✅ **আপলোড সফল!**\n\n"
            f"🔗 **লিংক:** [ক্লিক করে দেখুন]({upload_url})",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🌐 লিংক ওপেন করুন",
                            url=upload_url
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "📋 লিংক কপি করুন",
                            callback_data=f"copy_{upload_url}"
                        )
                    ]
                ]
            ),
            disable_web_page_preview=False
        )

        # টেম্প ফাইল ডিলিট
        try:
            os.remove(local_path)
        except:
            pass

    except Exception as e:
        await message.reply_text(f"❌ **এরর হয়েছে**\n\n**রিজন:** `{str(e)}`")
        try:
            os.remove(local_path)
        except:
            pass
        return

# ------------------------------------------------------------------------------- #

# কপি বাটনের জন্য কলব্যাক হ্যান্ডলার
@app.on_callback_query(filters.regex(r"^copy_"))
async def copy_link(client, callback_query):
    url = callback_query.data.replace("copy_", "")
    await callback_query.answer(f"🔗 লিংক: {url}", show_alert=True)

# ------------------------------------------------------------------------------- #

__HELP__ = """
**📸 টেলিগ্রাফ আপলোডার বট**

**কমান্ড সমূহ:**
• `/tgm` - রিপ্লাই করা মিডিয়া টেলিগ্রাফে আপলোড করে
• `/tgt` - একই কাজ করে
• `/telegraph` - একই কাজ করে
• `/tl` - একই কাজ করে

**📝 কিভাবে ব্যবহার করবেন:**
1. কোনো ফটো/ভিডিও/ডকুমেন্ট রিপ্লাই করুন
2. তারপর উপরের যেকোনো কমান্ড দিন
3. বাটন থেকে লিংক ওপেন বা কপি করুন

**⚠️ সীমাবদ্ধতা:**
• ম্যাক্স ফাইল সাইজ: ২০০MB
• সাপোর্টেড ফাইল: ফটো, ভিডিও, ডকুমেন্ট, GIF
"""

__MODULE__ = "ᴛᴇʟᴇɢʀᴀᴘʜ"

# ------------------------------------------------------------------------------- #