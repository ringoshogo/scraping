"""
①フロントサイドに渡す関数を定義
②eelの起動
"""

import eel
import desktop
import bsoup
from datetime import datetime
from common.fileio import CSVio


app_name="html"
end_point="index.html"
size=(800,600)

CTG_MST_PTH = "./master/category_master.csv"
AMZ_CTG_MST_PTH = "./master/amazon_url.csv"

@ eel.expose
def update_category(amazon_category_url):
    """カテゴリ情報を最新化する"""
    eel.writeLog(f"{datetime.now().strftime('%Y/%m/%d_%H:%M:%S')}-カテゴリの更新を開始しました。")
    category_list = bsoup.get_category_list(amazon_category_url)
    # マスタに最新のカテゴリを書き込む
    if category_list:
        CSVio.write_list_to_csv(CTG_MST_PTH, category_list)
        CSVio.write_list_to_csv(AMZ_CTG_MST_PTH, [["amazon_category_url"],[amazon_category_url]])
        eel.writeLog(f"{datetime.now().strftime('%Y/%m/%d_%H:%M:%S')}-カテゴリの更新が正常に終了しました。")
    else:
        eel.writeLog(f"{datetime.now().strftime('%Y/%m/%d_%H:%M:%S')}-カテゴリの更新に失敗しました。カテゴリ一覧のURLを再度ご確認ください。")
    return get_category_master()

@ eel.expose
def get_category_master():
    """マスタからカテゴリ情報を取得する"""
    return CSVio.read_csv_to_dict(CTG_MST_PTH)

@ eel.expose
def get_category_table_url_master():
    """マスタからカテゴリ一覧のURLを取得する"""
    return CSVio.read_csv_to_dict(AMZ_CTG_MST_PTH)

desktop.start(app_name,end_point,size)