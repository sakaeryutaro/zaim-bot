import json
import urllib.request


def url_request(url, headers, body):
    """

    :param url:HTTPリクエスト送信先url
    :param headers: HTTPリクエストヘッダー
    :param body: HTTPリクエストボディ
    :return:
    """
    # リクエストオブジェクトを作成
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    # urlopenにわたすことでリクエストを送信
    # with as構文を使うことでcloseしなくていい
    with urllib.request.urlopen(req) as res:
        body = json.loads(res.read())  # レスポンスボディ
        print(body)
