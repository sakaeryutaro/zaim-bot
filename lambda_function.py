import json
import os
from datetime import datetime
from datetime import timedelta

from url_request import url_request

# from zaim_api import zaim_delete_income
from zaim_api import zaim_delete_payment
from zaim_api import zaim_get_data
from zaim_api import zaim_insert_income
from zaim_api import zaim_insert_payment

# lineから送られてきたメッセージに対する応答先
url = "https://api.line.me/v2/bot/message/reply"
# リクエストヘッダー
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + os.getenv("LINE_CHANNEL_ACCESS_TOKEN"),  # LINEアクセストークン
}
# リクエストボディのテキスト
body_text = {
    "line_menu_reply": {
        "登録方法を確認": "1行目に支払方法、2行目にジャンル名、3行目に金額を入力してね\n\n"
        "■選択候補\n・支払方法：現金 or PayPay\n"
        "・ジャンル名：食費 or 生活費 or 娯楽費 or 特別費\n\n"
        "■入力例\n現金\n食費\n1000",
        "取消方法を確認": "1行目に「取消」、2行目に取消したい登録の登録IDを10桁の数字で入力してね\n\n■入力例\n取消\n1234567890",
    },
    "input_text_reply": {
        "register_success": "登録できたよ\n登録ID:",
        "register_error": "登録できなかったよ。もう1回登録してね",
        "cancel_success": "取消できたよ\n登録ID:",
        "cancel_error": "取消できなかったよ。もう1回取消してね",
        "input_error": "入力形式が正しくないよ。もう1回入力してね",
        "not_register": "登録データがないよ",
    },
}


# LINEに入力されたテキスト
input_text = {
    "register": {
        "account": ["現金", "PayPay"],
        "genre": ["食費", "生活費", "娯楽費", "仕事費", "特別費", "固定費", "その他"],
        "category": ["臨時収入", "立替金返済"],
    },
    "delete": {"operation": "取消"},
}


def lambda_handler(event, context):
    """
    json.loads()はJSON形式の文字列を辞書に変換
    lambdaはJSONを受け取ると全てeventに格納する(文字列型で)
    eventのbodyにlineからのリクエストボディが辞書型で格納される
    lineリクエストボディのeventsはリストの中に辞書が1つ格納されている
    for文でjson.loads(event["body"])["events"]を回すことで、リストから辞書だけを取り出せる
    :param event:
    :param context:
    :return:
    """

    for message_event in json.loads(event["body"])["events"]:
        # ユーザーが送付してきたlineメッセージを取得
        line_message = message_event["message"]["text"]
        # ユーザーが送付してきた日付を取得(UTCからJTCに変換)
        message_date = datetime.fromtimestamp(
            message_event["timestamp"] / 1000
        ) + timedelta(hours=9)
        # リクエストボデイ
        body = {
            "replyToken": message_event["replyToken"],
            "messages": [
                {
                    "type": "text",
                    "text": "",
                }
            ],
        }

        # メニューボタンが押されたときの返答
        for m in body_text["line_menu_reply"].keys():
            if line_message == m:
                body["messages"][0]["text"] = body_text["line_menu_reply"][line_message]
                url_request(url, headers, body)
        # 削除のとき
        if line_message.split()[0] == input_text["delete"]["operation"]:
            try:
                if (
                    len(line_message.split()[1]) == 10
                    and line_message.split()[1].isdecimal()
                ):
                    zaim_id_get_data = zaim_get_data()
                    if line_message.split()[1] in zaim_id_get_data:
                        zaim_res_status_code = zaim_delete_payment(
                            line_message.split()[1]
                        )
                        if zaim_res_status_code == 200:
                            body["messages"][0]["text"] = (
                                body_text["input_text_reply"]["cancel_success"]
                                + line_message.split()[1]
                            )
                            url_request(url, headers, body)
                        else:
                            body["messages"][0]["text"] = body_text["input_text_reply"][
                                "cancel_error"
                            ]
                            url_request(url, headers, body)
                    else:
                        body["messages"][0]["text"] = body_text["input_text_reply"][
                            "not_register"
                        ]
                        url_request(url, headers, body)
                else:
                    body["messages"][0]["text"] = body_text["input_text_reply"][
                        "input_error"
                    ]
                    url_request(url, headers, body)
            except (IndexError, KeyError):
                body["messages"][0]["text"] = body_text["input_text_reply"][
                    "input_error"
                ]
                url_request(url, headers, body)
        # 登録するとき
        elif line_message.split()[0] in input_text["register"]["account"]:
            try:
                if line_message.split()[1] in input_text["register"]["genre"]:
                    if line_message.split()[2].isdecimal():
                        # zaimに支払いデータの登録して、レスポンスを変数に格納
                        zaim_res_id, zaim_res_status_code = zaim_insert_payment(
                            message_date,
                            line_message.split()[2],
                            line_message.split()[1],
                            line_message.split()[0],
                        )
                        # zaimの登録に成功したら登録できたことを表示、できなかったら再度登録を促す
                        if zaim_res_status_code == 200:
                            body["messages"][0]["text"] = body_text["input_text_reply"][
                                "register_success"
                            ] + str(zaim_res_id)
                            url_request(url, headers, body)
                        else:
                            body["messages"][0]["text"] = body_text["input_text_reply"][
                                "register_error"
                            ]
                            url_request(url, headers, body)
                    else:
                        body["messages"][0]["text"] = body_text["input_text_reply"][
                            "input_error"
                        ]
                        url_request(url, headers, body)
                elif line_message.split()[1] in input_text["register"]["category"]:
                    if line_message.split()[2].isdecimal():
                        # zaimに支払いデータの登録して、レスポンスを変数に格納
                        zaim_res_id, zaim_res_status_code = zaim_insert_income(
                            message_date,
                            line_message.split()[1],
                            line_message.split()[2],
                            line_message.split()[0],
                        )
                        # zaimの登録に成功したら登録できたことを表示、できなかったら再度登録を促す
                        if zaim_res_status_code == 200:
                            body["messages"][0]["text"] = body_text["input_text_reply"][
                                "register_success"
                            ] + str(zaim_res_id)
                            url_request(url, headers, body)
                        else:
                            body["messages"][0]["text"] = body_text["input_text_reply"][
                                "register_error"
                            ]
                            url_request(url, headers, body)
                else:
                    body["messages"][0]["text"] = body_text["input_text_reply"][
                        "input_error"
                    ]
                    url_request(url, headers, body)
            except (IndexError, KeyError):
                body["messages"][0]["text"] = body_text["input_text_reply"][
                    "input_error"
                ]
                url_request(url, headers, body)
        else:
            body["messages"][0]["text"] = body_text["input_text_reply"]["input_error"]
            url_request(url, headers, body)
    return {"statusCode": 200}
