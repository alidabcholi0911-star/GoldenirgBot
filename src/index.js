const express = require("express");
const rubika = require("./rubika");
const { saveCode, getCode } = require("./db");

const ADMIN_ID = "u0Ic6ps06102e1a1969cc92b096f597e";
const PUBLIC_URL = ""; // بعد از گرفتن دامنه از Railway، اینجا پر کن

const app = express();
app.use(express.json());

const waitingForContent = new Set();

const ADMIN_START_TEXT =
  "سلااااااااااام حاج ممد 🫡\n" +
  "خوبی برار؟\n\n" +
  "نگاه حاجی جان من مدیریت فیلم‌ها رو گردن میگیرم، بقیه با تو 😄\n\n" +
  "نکنه توقع داری بیشتر از این‌ها کار کنم حاجیییی 😂\n" +
  "نه ممد خان، من همین کار رو گردن میگیرم 🙌\n\n" +
  "حالا گزینه زیر رو بزن ممد جان تا کد پیام رو بهت بدم 👇";

const ADMIN_KEYPAD = {
  rows: [
    {
      buttons: [
        { id: "make_code", type: "Simple", button_text: "🎬 ساخت کد" },
      ],
    },
  ],
};

app.post("/receiveUpdate", async (req, res) => {
  res.sendStatus(200);

  try {
    const update = req.body.update;
    if (!update) return;

    const chatId = update.chat_id;
    const msg = update.new_message;

    if (update.type === "StartedBot" || (msg && msg.text === "/start")) {
      if (chatId === ADMIN_ID) {
        await rubika.sendMessage(chatId, ADMIN_START_TEXT, ADMIN_KEYPAD);
      } else {
        await rubika.sendMessage(
          chatId,
          "سلام! 👋\nکد پیامی که داری رو برام بفرست تا محتوا رو نشونت بدم."
        );
      }
      return;
    }

    if (!msg) return;

    const buttonId = msg.aux_data && msg.aux_data.button_id;
    if (buttonId === "make_code") {
      if (chatId !== ADMIN_ID) return;
      waitingForContent.add(chatId);
      await rubika.sendMessage(
        chatId,
        "خب حاج ممد 😎\n" +
          "الان ۹۹ درصد راه رو رفتی.\n" +
          "حالا میخوای کاربرا وقتی کد رو زدن چی نشونشون بدم؟\n" +
          "بفرست برام حاج ممد خان (متن، عکس، فیلم یا فایل، هرچی باشه) 📥"
      );
      return;
    }

    if (chatId === ADMIN_ID && waitingForContent.has(chatId)) {
      let code;

      if (msg.file && msg.file.file_id) {
        code = saveCode({
          type: "file",
          fileId: msg.file.file_id,
          caption: msg.text || "",
        });
      } else if (msg.text) {
        code = saveCode({ type: "text", content: msg.text });
      } else {
        await rubika.sendMessage(
          chatId,
          "این نوع پیام رو نمی‌شناسم 🙏 یه متن یا فایل بفرست."
        );
        return;
      }

      waitingForContent.delete(chatId);
      await rubika.sendMessage(
        chatId,
        `دیدی ناموسا چقددددددر راحت 😎\n\nکد پیامت میشه:\n\n${code}\n\n` +
          "حالا هر کاربری این کد رو بزنه، همون پیام رو نشونش میدم."
      );
      return;
    }

    if (msg.text) {
      const record = getCode(msg.text.trim());
      if (record) {
        if (record.type === "text") {
          await rubika.sendMessage(chatId, record.content);
        } else {
          await rubika.sendFile(chatId, record.file_id, record.caption || "");
        }
      } else {
        await rubika.sendMessage(chatId, "کد اشتباهه ❌ دوباره چک کن.");
      }
    }
  } catch (err) {
    console.error("خطا در پردازش آپدیت:", err.message);
  }
});

app.get("/", (req, res) => res.send("Rubika bot is running ✅"));

const PORT = process.env.PORT || 3000;
app.listen(PORT, async () => {
  console.log(`Server running on port ${PORT}`);

  if (PUBLIC_URL) {
    try {
      const res = await rubika.updateBotEndpoint(
        `${PUBLIC_URL.replace(/\/$/, "")}/receiveUpdate`,
        "ReceiveUpdate"
      );
      console.log("وبهوک با موفقیت ثبت شد:", res);
    } catch (err) {
      console.error("ثبت خودکار وبهوک شکست خورد:", err.message);
    }
  } else {
    console.log("PUBLIC_URL هنوز خالیه — بعد از گرفتن دامنه از Railway پرش کن.");
  }
});
