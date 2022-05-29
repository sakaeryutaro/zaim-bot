import os

from pyzaim import ZaimAPI

# zaimのAPI認証
api = ZaimAPI(
    os.getenv("ZAIM_CONSUMER_ID"),  # zaimコンシューマID
    os.getenv("ZAIM_CONSUMER_SECRET"),  # zaimコンシューマシークレット
    os.getenv("ZAIM_ACCESS_TOKEN"),  # zaimアクセストークン
    os.getenv("ZAIM_ACCESS_SECRET"),  # zaimアクセスシークレット
    os.getenv("ZAIM_VERIFIER"),  # zaim verifier
)


def zaim_insert_payment(date, amount, genre, account):
    # zaimに支払いデータの登録して、レスポンスを変数に格納
    zaim_res = api.insert_payment_simple(
        date,  # 日付
        amount,  # 金額
        genre,  # ジャンル名
        account,  # 口座名
    )
    # 登録したIDを取得
    zaim_res_id = zaim_res.json()["money"]["id"]
    # レスポンスのステータスコートを取得
    zaim_res_status_code = zaim_res.status_code
    return zaim_res_id, zaim_res_status_code


def zaim_delete_payment(register_id):
    zaim_res = api.delete_payment(register_id)
    # レスポンスのステータスコートを取得
    zaim_res_status_code = zaim_res.status_code
    return zaim_res_status_code


def zaim_insert_income(date, category, amount, account):
    # zaimに支払いデータの登録して、レスポンスを変数に格納
    zaim_res = api.insert_income_simple(
        date,  # 日付
        category,  # カテゴリ
        amount,  # 金額
        account,  # 口座名
    )
    # 登録したIDを取得
    zaim_res_id = zaim_res.json()["money"]["id"]
    # レスポンスのステータスコートを取得
    zaim_res_status_code = zaim_res.status_code
    return zaim_res_id, zaim_res_status_code


# def zaim_delete_income(register_id):
#     zaim_res = api.delete_income(register_id)
#     # レスポンスのステータスコートを取得
#     zaim_res_status_code = zaim_res.status_code
#     return zaim_res_status_code


def zaim_get_data():
    zaim_data = api.get_data()
    zaim_id_data = [str(i["id"]) for i in zaim_data]
    return zaim_id_data
