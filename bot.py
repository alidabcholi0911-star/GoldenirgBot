import time

import rubika
import db

ADMIN_IDS = {
    "b0Ic6ps0BEVi0f3e9f113b9e909f6265",
    "b0Ic6ps0ZUz00069305e4008836aca1e",
    "u0Ic6ps06102e1a1969cc92b096f597e",
}


def find_file_id(msg):
    for key, value in msg.items():
        if isinstance(value, dict):
            if value.get("file_id"):
                return value.get("file_id")
    return None


def is_from_admin(update, msg):
    candidates = set()
    if update.get("chat_id"):
        candidates.add(update.get("chat_id"))
    if update.get("object_guid"):
        candidates.add(update.get("object_guid"))
    if msg is not None:
        if msg.get("sender_id"):
            candidates.add(msg.get("sender_id"))
        if msg.get("author_guid"):
            candidates.add(msg.get("author_guid"))
    return len(candidates.intersection(ADMIN_IDS)) > 0

ADMIN_START_TEXT = (
    "سلااااااااااام حاج ممد 🫡\n"
    "خوبی برار؟\n\n"
    "نگاه حاجی جان من مدیریت فیلم‌ها رو گردن میگیرم، بقیه با تو 😄\n\n"
    "نکنه توقع داری بیشتر از این‌ها کار کنم حاجیییی 😂\n"
    "نه ممد خان، من همین کار رو گردن میگیرم 🙌\n\n"
    "حالا پیام بفرست تا کد تحویل بگیری 👇"
)

USER_START_TEXT = (
    "به ربات بزرگترین مجموعه آموزش ارگ اندروید دانلود خوش آمدید 🎹\n\n"
    "به گلدن ارگ خوش آمدید 🌟\n\n"
    "خوشحالیم که ما رو برای یادگیری انتخاب کردین 🙏\n\n"
    "ما در تلاشیم که با کمترین هزینه بهترین آموزش رو بهتون بدیم 💛\n\n"
    "لطفا کدی از کانال @org_androidVIP گرفتین رو ارسال کنید تا پیام مربوط به کد را برای شما ارسال کنم 🔑"
)


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
            if is_from_admin(update, msg):
                rubika.send_message(chat_id, ADMIN_START_TEXT)
            else:
                rubika.send_message(chat_id, USER_START_TEXT)
            return

        if msg is None:
            return

        if msg.get("text") == "/myid":
            rubika.send_message(chat_id, "شناسه شما: " + str(chat_id))
            return

        if is_from_admin(update, msg):
            found_file_id = find_file_id(msg)

            if found_file_id:
                caption = ""
                if msg.get("text"):
                    caption = msg.get("text")
                code = db.save_code("file", file_id=found_file_id, caption=caption)
            elif msg.get("text"):
                code = db.save_code("text", content=msg.get("text"))
            else:
                code = db.save_code("text", content=str(msg))

            rubika.send_message(
                chat_id,
                "خب حاجی بیا اینم کد پیامت 😎\n\n"
                + code
                + "\n\nحالا کاربرانت این کد بزنه پیامت نشون میده",
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
    offset_id = db.get_setting("last_offset_id")
    print("ربات با polling شروع به کار کرد...")
    while True:
        try:
            res = rubika.get_updates(limit=50, offset_id=offset_id)
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
                db.set_setting("last_offset_id", offset_id)
        except Exception as error:
            print("خطا در polling:", error)

        time.sleep(0.5)


if __name__ == "__main__":
    poll()
