import time

import rubika
import db

ADMIN_ID = "b0Ic6ps0ZUz00069305e4008836aca1e"

waiting_for_content = set()

ADMIN_START_TEXT = (
    "سلااااااااااام حاج ممد 🫡\n"
    "خوبی برار؟\n\n"
    "نگاه حاجی جان من مدیریت فیلم‌ها رو گردن میگیرم، بقیه با تو 😄\n\n"
    "نکنه توقع داری بیشتر از این‌ها کار کنم حاجیییی 😂\n"
    "نه ممد خان، من همین کار رو گردن میگیرم 🙌\n\n"
    "حالا گزینه زیر رو بزن ممد جان تا کد پیام رو بهت بدم 👇"
)

USER_START_TEXT = (
    "به ربات بزرگترین مجموعه آموزش ارگ اندروید دانلود خوش آمدید 🎹\n\n"
    "به گلدن ارگ خوش آمدید 🌟\n\n"
    "خوشحالیم که ما رو برای یادگیری انتخاب کردین 🙏\n\n"
    "ما در تلاشیم که با کمترین هزینه بهترین آموزش رو بهتون بدیم 💛\n\n"
    "لطفا کدی از کانال @org_androidVIP گرفتین رو ارسال کنید تا پیام مربوط به کد را برای شما ارسال کنم 🔑"
)

ADMIN_KEYPAD = {
    "rows": [
        {
            "buttons": [
                {"id": "make_code", "type": "Simple", "button_text": "🎬 ساخت کد"}
            ]
        }
    ]
}


def handle_update(update):
    try:
        chat_id = update.get("chat_id")
        msg = update.get("new_message")

        is_start = False
        if update.get("type") == "StartedBot":
            is_start = True
        if msg is not None:
            if msg.get("text") == "/start":
                is_start = True

        if is_start:
            if chat_id == ADMIN_ID:
                rubika.send_message(chat_id, ADMIN_START_TEXT, ADMIN_KEYPAD)
            else:
                rubika.send_message(chat_id, USER_START_TEXT)
            return

        if msg is None:
            return

        button_id = None
        aux_data = msg.get("aux_data")
        if aux_data is not None:
            button_id = aux_data.get("button_id")

        if button_id == "make_code":
            if chat_id != ADMIN_ID:
                return
            waiting_for_content.add(chat_id)
            rubika.send_message(
                chat_id,
                "خب حاج ممد 😎\n"
                "الان ۹۹ درصد راه رو رفتی.\n"
                "حالا میخوای کاربرا وقتی کد رو زدن چی نشونشون بدم؟\n"
                "بفرست برام حاج ممد خان (متن، عکس، فیلم یا فایل، هرچی باشه) 📥",
            )
            return

        if chat_id == ADMIN_ID and chat_id in waiting_for_content:
            file_data = msg.get("file")
            has_file = False
            if file_data is not None:
                if file_data.get("file_id"):
                    has_file = True

            if has_file:
                caption = ""
                if msg.get("text"):
                    caption = msg.get("text")
                code = db.save_code("file", file_id=file_data.get("file_id"), caption=caption)
            elif msg.get("text"):
                code = db.save_code("text", content=msg.get("text"))
            else:
                rubika.send_message(
                    chat_id, "این نوع پیام رو نمی‌شناسم 🙏 یه متن یا فایل بفرست."
                )
                return

            waiting_for_content.discard(chat_id)
            rubika.send_message(
                chat_id,
                "دیدی ناموسا چقددددددر راحت 😎\n\nکد پیامت میشه:\n\n"
                + code
                + "\n\nحالا هر کاربری این کد رو بزنه، همون پیام رو نشونش میدم.",
            )
            return

        if msg.get("text"):
            record = db.get_code(msg.get("text").strip())
            if record is not None:
                if record["type"] == "text":
                    rubika.send_message(chat_id, record["content"])
                else:
                    caption = ""
                    if record["caption"]:
                        caption = record["caption"]
                    rubika.send_file(chat_id, record["file_id"], caption)
            else:
                rubika.send_message(chat_id, "کد اشتباهه ❌ دوباره چک کن.")
    except Exception as error:
        print("خطا در پردازش آپدیت:", error)


def poll():
    offset_id = None
    print("ربات با polling شروع به کار کرد...")
    while True:
        try:
            res = rubika.get_updates(limit=50, offset_id=offset_id)
            print("پاسخ خام روبیکا:", res)
            data = {}
            if res:
                if res.get("data"):
                    data = res.get("data")

            updates = data.get("updates")
            if not updates:
                updates = data.get("chat_updates")
            if not updates:
                updates = []

            for update in updates:
                handle_update(update)

            if data.get("next_offset_id"):
                offset_id = data.get("next_offset_id")
        except Exception as error:
            print("خطا در polling:", error)

        time.sleep(0.5)


if __name__ == "__main__":
    poll()
