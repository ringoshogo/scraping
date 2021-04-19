import time
import os

from common.driver import Driver
from common.fileio import CSVio
from common.logger import set_logger
from selenium.webdriver.common.by import By

# ログの設定(モジュール名の設定)
logger = set_logger(__name__)

# amazonランキングのセールストップ画面
RNK_TOP_URL = "https://www.amazon.co.jp/gp/bestsellers/ref=zg_bs_tab"

CSV_ROOT_URL = os.getcwd() + "/result/"

def scraping_all():
    """amazonの全カテゴリの情報を取得する"""

    driver = Driver(False)

    # ランキングトップページへ遷移
    driver.get(RNK_TOP_URL)
    driver.wait_until_presence_of_all_elements_located()
    time.sleep(1)

    # 遷移先を取得
    category_dict = {}
    category_elems = driver.find_element(By.ID, "zg_browseRoot").find_elements(By.TAG_NAME, "a")
    for elem in category_elems:
        # 遷移先を辞書形式で取得。{カテゴリ名: url}
        category_dict[elem.text] = elem.get_attribute("href")

    # カテゴリごとに処理を実施
    for k, v in category_dict.items():
        # k=カテゴリ名, v=url

        # 【カテゴリ別商品一覧】商品別に値を取得する
        result_list = [["category", "ranking", "name", "price", "isprime", "stock", "delivery", "ASIN"]]
        item_list = []

        # CSVpath
        csv_path = CSV_ROOT_URL + k + ".csv"

        # カテゴリ別商品一覧画面の情報を取得する
        _get_item_overview_info(driver, v, k, item_list)
        _get_item_overview_info(driver, v + "&pg=2", k, item_list)

        for item in item_list:

            # 商品詳細情報を取得する
            _get_item_detail_info(driver, item, k, result_list)

        CSVio.write_list_to_csv(csv_path, result_list)

        break

def scraping(url):
    """指定の商品カテゴリ一覧ページの情報を取得する"""
    pass


def _get_item_overview_info(driver, category_url, category, item_list):
    """カテゴリ別商品一覧ページの情報を取得する"""
    # カテゴリ別商品一覧画面に遷移する
    driver.get(category_url)
    driver.wait_until_presence_of_all_elements_located()
    items_elems = driver.find_elements(By.CLASS_NAME, "zg-item-immersion")

    # カテゴリ別商品一覧画面の情報を取得する
    for i, item_elem in enumerate(items_elems):

        try:
            item_dict = {}
            # ランキング
            item_dict['rank'] = item_elem.find_element(By.CLASS_NAME, "zg-badge-text").text.strip()
            
            item_link = item_elem.find_element(By.CSS_SELECTOR, "span > div > span > a")
            # 商品名
            item_dict['item_name'] = item_link.text.strip()
            # 商品詳細リンク先
            item_dict['href'] = item_link.get_attribute("href")
            item_list.append(item_dict)
        except Exception as err:
            print(err)
            logger.info(f"カテゴリ:{category} > {i+1}個目のアイテム概要取得に失敗しました。")


def _get_item_detail_info(driver, item, category, result_list):
    """商品詳細ページの情報を取得する"""
    # 商品詳細画面に遷移する
    driver.get(item['href'])
    driver.wait_until_presence_of_all_elements_located()
    time.sleep(1)

    # 商品価格
    # item["price"] = _get_item_detail(lambda: driver.find_element(By.ID, "priceblock_ourprice").text.strip(), category, item['item_name'], "price", "-")
    price = _get_item_detail(lambda: driver.find_element(By.ID, "priceblock_ourprice").text.strip(), category, item['item_name'], "price", "-")
    # プライムか否か
    is_prime_elems = _get_item_detail(lambda: driver.find_elements(By.CSS_SELECTOR, "#priceBadging_feature_div > i > i"), category, item['item_name'], "is_prime", 0)
    # item["is_prime"] = 1 if len(is_prime_elems) > 0 else 0
    is_prime = 1 if len(is_prime_elems) > 0 else 0
    # 在庫
    availability = _get_item_detail(lambda: driver.find_elements(By.CSS_SELECTOR, "#availability > span")[0].text.strip(), category, item['item_name'], "availability", "在庫無し。")
    # item["availability"] = 1 if "在庫あり。" == availability else 0
    availability = 1 if "在庫あり。" == availability else 0
    # お届け日
    delivery = _get_item_detail(lambda: driver.find_element(By.CSS_SELECTOR, "#ddmDeliveryMessage > b").text.strip(), category, item['item_name'], "delivery", "-")
    # item["delivery"] = _get_item_detail(lambda: driver.find_element(By.CSS_SELECTOR, "#ddmDeliveryMessage > b").text.strip(), category, item['item_name'], "delivery", "-")
    # ASIN
    asin = _get_item_detail(lambda: driver.find_element(By.CSS_SELECTOR, "#productDetails_detailBullets_sections1 > tbody > tr:nth-child(1) > td").text.strip(), category, item['item_name'], "delivery", "-")
    # item["asin"] = _get_item_detail(lambda: driver.find_element(By.CSS_SELECTOR, "#productDetails_detailBullets_sections1 > tbody > tr:nth-child(1) > td").text.strip(), category, item['item_name'], "delivery", "-")

    result_list.append([category, item['rank'], item['item_name'], price, is_prime, availability, delivery, asin])

def _get_item_detail(func, category, item_name, item_col, default):
    """引数のカラムの値を取得する"""
    try:
        return func()
    except Exception as err:
        logger.info(f"カテゴリ:{category} > 商品名:{item_name} > カラム:{item_col}の取得に失敗しました。error:{err}")
        return default



if __name__ == "__main__":
    scraping_all()

