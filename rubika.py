import requests

TOKEN = "CEDBIJ0IODNFFVMQLXUCPGSIJNSNCMAPTDHFIRRJZBXRIOZUYMAIDHURUAHZQNMN"

BASE_URL = "https://botapi.rubika.ir/v3/" + TOKEN


def call_method(method, params=None):
    if params is None:
        params = {}
    url = BASE_URL + "/" + method
    response = requests.post(url, json=params, timeout=15)
    print("درخواست به:", url)
    print("وضعیت پاسخ:", response.status_code)
    print("متن خام پاسخ:", response.text)
    return response.json()


def send_message(chat_id, text, inline_keypad=None):
    params = {"chat_id": chat_id, "text": text}
    if inline_keypad is not None:
        params["inline_keypad"] = inline_keypad
    return call_method("sendMessage", params)


def send_file(chat_id, file_id, caption=""):
    params = {"chat_id": chat_id, "file_id": file_id, "text": caption}
    return call_method("sendFile", params)


def get_updates(limit=10, offset_id=None):
    params = {"limit": limit}
    if offset_id is not None:
        params["offset_id"] = offset_id
    return call_method("getUpdates", params)


def forward_message(from_chat_id, message_id, to_chat_id):
    params = {
        "from_chat_id": from_chat_id,
        "message_id": message_id,
        "to_chat_id": to_chat_id,
    }
    return call_method("forwardMessage", params)
