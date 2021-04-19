from .singleton import Singleton
import time

import os
import errno
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# 待機用
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert

# ロガーの設定
from common.logger import set_logger
logger = set_logger(__name__)

# web要素へのアクション
ACTION_TYPE_CLICK = 1
ACTION_TYPE_GET_URL = 2

class Driver(Singleton):
    """ウェブドライバーを操作するクラス"""

    def __init__(self, headless_flg):

        # 既にドライバーを作成済みの場合、事前に閉じる
        print("has attr driver", hasattr(self, 'driver'))
        if hasattr(self, 'driver'):
            self.driver.quit()

        #chromeドライバーの読込
        options = webdriver.ChromeOptions()

        # ヘッドレスモード（画面非表示モード）をの設定
        if headless_flg == True:
            options.add_argument('--headless')

        # 起動オプションの設定
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
        
        # profile を作成する場合
        userdata_dir = "UserData"
        if not os.path.exists(userdata_dir):
            os.makedirs(userdata_dir, exist_ok=True)

        # options.add_argument('log-level=3')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--user-data-dir=' + userdata_dir)

        #options.add_argument('--incognito')          # シークレットモードの設定を付与

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    def get(self, url):
        """引数指定のURLに遷移する"""
        self.driver.get(url)

    def find_element(self, tag_type, name):
        """htmlタグに 指定したtype=nemaとなる要素の1つ目を返却する。"""
        elements = self.driver.find_elements(tag_type, name)
        if elements:
            return elements[0]
        return False

    def find_elements(self, tag_type, name):
        """htmlタグに 指定したtype=nemaとなる要素をリスト形式で返却する。"""
        return self.driver.find_elements(tag_type, name)

    def wait_until_alert_and_accept(self):
        """アラートが表示されるまで待機する"""
        try:
            WebDriverWait(self.driver, 30).until(
                # アラートが表示されるまで待機
                EC.alert_is_present()
            )
            time.sleep(2)
            Alert(self.driver).accept()

        except TimeoutException as err:
            logger.error("30秒経ってもアラートポップアップを確認できませんでした。")
            raise TimeoutException(err)
        

    def wait_until_presence_of_all_elements_located(self):
        """全ての要素が読みこまれるまで待機する"""
        try:
            WebDriverWait(self.driver, 30).until(
                # 全ての要素が読み込まれるまで待機
                EC.presence_of_all_elements_located
            )

        except TimeoutException as err:
            logger.error("30秒経ってもページを読みこむ事ができませんでした。")
            raise TimeoutException(err)

    def wait_until_located(self, tag_type, name, wait_time):
        """引数指定の type=name が現れるまで wait_time秒待機する"""
        
        while True:

            loop_flg = False    
            try:
                # 300秒待機する
                WebDriverWait(self.driver, wait_time).until(
                    EC.element_to_be_clickable((tag_type, name))
                )
            except TimeoutException as err:
                logger.error(f"{wait_time}秒経ってもタイプ：{tag_type}名前：{name}を確認できませんでした。error:{err.args}")
                raise TimeoutException(err)
            except UnexpectedAlertPresentException as err:
                loop_flg = True
                time.sleep(2)

            if not loop_flg:
                break

    def goto_a_tag_url(self, xpath, action_type=ACTION_TYPE_GET_URL):
        """xpath の値により aタグのリンク先に遷移する"""
        try:
            a_tag_list = self.driver.find_elements_by_xpath(xpath)
            
            # 指定の名前のxpathが存在する場合
            if a_tag_list:

                if action_type == ACTION_TYPE_GET_URL:
                    # リンク先に遷移する
                    url = a_tag_list[0].get_attribute("href")
                    self.driver.get(url)
                else:
                    # ボタンをクリックする
                    a_tag_list[0].click()
                    
                time.sleep(2)
            
            else:
                logger.error(f"xpath: {xpath} は存在しませんでした。")

        except Exception as err:
            logger.error(f"xpath: {xpath} 取得時に例外が発生しました。error:{err.args}")

    def send_image_to_input_tag(self, image_path, id_name, item_name, index):
        """指定のインプットタグに画像を送信する"""

        if os.path.exists(image_path):
            image_elem = self.driver.find_elements(By.ID, id_name)[0]
            time.sleep(1)
            image_elem.send_keys(image_path)

        else:
            logger.error(f"商品名：{item_name} > 画像{index}枚目：ファイル名：{image_path}は存在しません。")
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), image_path)
        

    def execute_script(self, onclickmethod, option=None):
        """javascript の メソッドを呼び出す"""
        if option:
            self.driver.execute_script(onclickmethod, option)
        else:
            self.driver.execute_script(onclickmethod)


    def quit(self):
        """処理を終了する"""
        self.driver.quit()