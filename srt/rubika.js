const axios = require("axios");

const TOKEN = "CEDBIJ0IODNFFVMQLXUCPGSIJNSNCMAPTDHFIRRJZBXRIOZUYMAIDHURUAHZQNMN";

const BASE_URL = `https://messengerg2b1.iranlms.ir/v3/${TOKEN}`;

async function callMethod(method, params = {}) {
  try {
    const { data } = await axios.post(`${BASE_URL}/${method}`, params, {
      timeout: 15000,
    });
    return data;
  } catch (err) {
    const detail = err.response ? JSON.stringify(err.response.data) : err.message;
    console.error(`[rubika] خطا در متد ${method}:`, detail);
    throw err;
  }
}

function sendMessage(chatId, text, inlineKeypad = null) {
  const params = { chat_id: chatId, text };
  if (inlineKeypad) params.inline_keypad = inlineKeypad;
  return callMethod("sendMessage", params);
}

function sendFile(chatId, fileId, caption = "") {
  return callMethod("sendFile", {
    chat_id: chatId,
    file_id: fileId,
    text: caption,
  });
}

function updateBotEndpoint(url, type = "ReceiveUpdate") {
  return callMethod("updateBotEndpoint", { url, type });
}

function getMe() {
  return callMethod("getMe", {});
}

module.exports = {
  callMethod,
  sendMessage,
  sendFile,
  updateBotEndpoint,
  getMe,
};
