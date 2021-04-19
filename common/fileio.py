import gspread
import json
import requests
import csv
from .singleton import Singleton

from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd

# ロガーの設定
from common.logger import set_logger
logger = set_logger(__name__)

#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
JSONKEY = './secrets/my-project-8844405-05992ddf0789.json'

class GspreadHandler(Singleton):
    """グーグルスプレッドシートを操作するクラス"""
    
    def __init__(self):

        #認証情報設定
        #ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
        credentials = ServiceAccountCredentials.from_json_keyfile_name(JSONKEY, SCOPE)
        #OAuth2の資格情報を使用してGoogle APIにログインします。
        self.gc = gspread.authorize(credentials)

    def get_worksheet_as_df(self, url):
        """引数指定のワークブックURLの情報をpandasとして取得する"""
        # シートの1番目を指定する
        worksheet = self.gc.open_by_url(url).get_worksheet(0)
        df = pd.DataFrame(worksheet.get_all_values())
        df.columns = list(df.loc[0, :]) # valuesの1行目をcolumnsとして指定
        df.drop(0, inplace=True) # valuesの1行目(0番目のデータ)を削除
        df.reset_index(inplace=True) # 
        df.drop('index', axis=1, inplace=True)
        return df.set_index("#")


if __name__ == "__main__":
    pass

class CSVio:
    """csvファイルへの書き込みを実施するクラス"""

    @staticmethod
    def write_list_to_csv(target_path: str, target_list: list):
        """引数指定のURLに文字列をcsv形式で書き込む"""
        try:
            with open(target_path, mode='w', encoding='utf-8_sig', newline="") as f:
                writer = csv.writer(f)
                writer.writerows(target_list)
        except IOError as e:
            logger.error("ファイルに書き込みができませんでした。")