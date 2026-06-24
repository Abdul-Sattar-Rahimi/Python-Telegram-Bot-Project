# ============================================================
#   مرحله ۱: این سل رو اول اجرا کن (نصب کتابخونه‌ها)
# ============================================================
# !pip install python-telegram-bot==20.7 jdatetime nest_asyncio

# ============================================================
#   مرحله ۲: این سل رو اجرا کن (کد اصلی ربات)
# ============================================================

import nest_asyncio
nest_asyncio.apply()

import logging
import random
import asyncio
from datetime import datetime

import jdatetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

# ─────────────────────────────────────────────
# 🔑  توکن ربات خودت رو اینجا بذار
# ─────────────────────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# ─────────────────────────────────────────────
# وضعیت فعال/غیرفعال بودن ربات در هر گروه
# ─────────────────────────────────────────────
active_groups = {}

# ─────────────────────────────────────────────
# محتوا
# ─────────────────────────────────────────────
JOKES = [
    "یه نفر رفت دکتر گفت: دکتر هر چیزی می‌خورم معده‌ام درد می‌گیره!\nدکتر گفت: پس چیزی نخور!\nگفت: اونم امتحان کردم، اونم درد می‌گیره! 😂",
    "معلم: بچه‌ها، کی می‌تونه یه جمله با کلمه «اگر» بسازه؟\nعلی: اگر من درس بخونم، مامانم شاکی میشه که مریضم! 😅",
    "رفتم خونه دوستم، دیدم داره گریه می‌کنه.\nگفتم: چی شده؟\nگفت: مامانم گفت دوستات مثل خودتن!\nگفتم: خب؟\nگفت: یعنی همه بی‌خودن! 😂",
    "پسره به باباش: بابا یه موتور می‌خوام!\nبابا: نه، خطرناکه.\nپسره: پس یه ماشین؟\nبابا: نه، گرونه.\nپسره: پس یه دوچرخه؟\nبابا: باشه!\nپسره: ممنون بابا... دوچرخه‌ات رو! 😁",
    "دو تا موش داشتن از گربه فرار می‌کردن.\nیکیشون گفت: فکر کنم گیر افتادیم!\nاون یکی گفت: صبر کن...\nبعد واق واق کرد، گربه ترسید و رفت!\nگفت: دیدی؟ یه زبون خارجه بلد بودن چقدر مفیده! 😂",
    "استاد دانشگاه: چرا دیر اومدی؟\nدانشجو: تصادف کردم.\nاستاد: با کی؟\nدانشجو: با خواب! 😴😂",
    "مامانم گفت: برو اتاقت رو مرتب کن!\nرفتم، یه ساعت بعد اومدم بیرون.\nگفت: مرتب کردی؟\nگفتم: نه، ولی با وسایلام آشتی کردم! 😂",
    "دکتر به بیمار: باید روزی ۳ بار قرص بخوری.\nبیمار: قبل از غذا یا بعدش؟\nدکتر: هر وقت غذا خوردی!\nبیمار: آخه من روزی یه بار غذا می‌خورم!\nدکتر: خب، قرصم یه بار بخور! 😅",
    "به تاکسی گفتم: آقا تند برو، دیرم شده!\nراننده: چشم!\n۲۰ دقیقه بعد: آقا چرا نمی‌ری؟\nراننده: گفتی تند برم، نگفتی حرکت کنم! 😂",
    "رفتم آرایشگاه گفتم: موهامو مثل مسی کن!\nآرایشگر نگاهم کرد، گفت: پس کچل کنم؟! 😅⚽",
]

PROVERBS = [
    "🌿 کار نیکو کردن از پر کردن است.",
    "🌿 عجول را پشیمانی در پی است.",
    "🌿 هر که بامش بیش، برفش بیشتر.",
    "🌿 دوست آن است که گیرد دست دوست / در پریشان‌حالی و درماندگی.",
    "🌿 کندی و پیوستگی، کار را به انجام می‌رساند.",
    "🌿 آدم حسابی از سنگ هم حساب می‌کشد.",
    "🌿 هر که طاووس خواهد، جور هندوستان کشد.",
    "🌿 از تو حرکت، از خدا برکت.",
    "🌿 دانش بهتر از گنج است؛ دانش نگهبان توست، تو نگهبان گنج.",
    "🌿 مرغ همسایه غاز به نظر می‌رسد.",
]

CHALLENGES = [
    "🎯 چالش: امروز به ۳ نفر که دوستشون داری یه پیام محبت‌آمیز بفرست!",
    "🎯 چالش: ۲۰ تا دراز-نشست انجام بده و نتیجه رو اینجا بنویس!",
    "🎯 چالش: یه کار خیر ناشناس امروز انجام بده و فقط به خودت بگو!",
    "🎯 چالش: بدون گوشی ۱ ساعت کامل وقت بگذرون و تجربه‌ات رو بنویس!",
    "🎯 چالش: یه غذای جدید که تا حالا نپختی امروز درست کن!",
    "🎯 چالش: ۳۰ ثانیه با آب سرد دوش بگیر! 🥶",
    "🎯 چالش: امروز به جای آسانسور از پله استفاده کن!",
    "🎯 چالش: یه کتاب یا مقاله که مدتیه داری به تعویق میندازی، همین امروز شروع کن!",
    "🎯 چالش: ۵ دقیقه مدیتیشن یا تنفس عمیق انجام بده!",
    "🎯 چالش: با یه نفر که مدتیه باهاش حرف نزدی تماس بگیر!",
]

HIJRI_MONTHS = [
    "محرم", "صفر", "ربیع‌الاول", "ربیع‌الثانی",
    "جمادی‌الاول", "جمادی‌الثانی", "رجب", "شعبان",
    "رمضان", "شوال", "ذی‌القعده", "ذی‌الحجه",
]

def gregorian_to_hijri(year, month, day):
    jd = (367 * year
          - int(7 * (year + int((month + 9) / 12)) / 4)
          + int(275 * month / 9)
          + day + 1721013.5)
    z = jd - 1948438.5
    cycle, remainder = divmod(z, 10631)
    year_h = int(30 * cycle + (remainder / 354.367))
    jd1 = 1948439.5 + 354 * year_h + int((11 * year_h + 3) / 30)
    month_h = int((jd - jd1) / 29.5) + 1
    day_h = int(jd - jd1 - 29.5 * (month_h - 1)) + 1
    if month_h > 12:
        month_h = 12
    if day_h < 1:
        day_h = 1
    return int(year_h), int(month_h), int(day_h)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    chat_id = msg.chat_id
    text = msg.text.strip()

    if text == "#فعال":
        active_groups[chat_id] = True
        await msg.reply_text("✅ ربات فعال شد! حالا می‌تونی از دستورات استفاده کنی.")
        return

    if not active_groups.get(chat_id, False):
        return

    if text == "جوک":
        await msg.reply_text(random.choice(JOKES))

    elif text == "ضرب المثل":
        await msg.reply_text(random.choice(PROVERBS))

    elif text == "تاس":
        dice = random.randint(1, 6)
        faces = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣"}
        await msg.reply_text(f"🎲 تاس انداختم: {faces[dice]}  ({dice})")

    elif text == "تاریخ":
        now = datetime.now()
        miladi = now.strftime("%Y/%m/%d")
        jdate = jdatetime.date.fromgregorian(day=now.day, month=now.month, year=now.year)
        shamsi = jdate.strftime("%Y/%m/%d")
        h_y, h_m, h_d = gregorian_to_hijri(now.year, now.month, now.day)
        qamari = f"{h_y}/{h_m:02d}/{h_d:02d}  ({HIJRI_MONTHS[h_m - 1]})"
        response = (
            f"📅 تاریخ امروز:\n\n"
            f"🗓 میلادی:  {miladi}\n"
            f"🌙 شمسی:   {shamsi}\n"
            f"☪️ قمری:   {qamari}"
        )
        await msg.reply_text(response)

    elif text == "چالش":
        await msg.reply_text(random.choice(CHALLENGES))


async def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ ربات شروع به کار کرد!")
    print("📌 برای فعال‌سازی در گروه، پیام #فعال ارسال کن")
    await app.run_polling()


asyncio.get_event_loop().run_until_complete(main())
