# BeautifulSoupを使用してのスクレイピング

import requests
import re
from bs4 import BeautifulSoup
import time

import os
import asyncio

from common.logger import set_logger
from common.fileio import CSVio
from common.driver import Driver

logger = set_logger(__name__)

# amazonランキングのセールストップ画面
RNK_TOP_URL = "https://www.amazon.co.jp/gp/bestsellers/ref=zg_bs_tab"

CSV_ROOT_URL = os.getcwd() + "/result/"

def scraping_all_bybs4():
    """全カテゴリのスクレイピング"""

    # ドライバを起動
    driver = Driver(True)

    try:
        # 全カテゴリのカテゴリ名： URLを保持する
        category_dict = get_category_dict(RNK_TOP_URL, driver)

        # 各カテゴリごとに商品情報を取得する
        for category_name, href in category_dict.items():

            # csvに出力するリストを作成
            result_list = [["category", "ranking", "name", "price", "isprime", "stock", "delivery", "ASIN"]]
            item_list = []

            # 出力するCSVパス
            csv_path = CSV_ROOT_URL + category_name + ".csv"

            # カテゴリ別商品一覧画面の情報を取得する
            _get_item_overview_info(driver, href, category_name, item_list)
            _get_item_overview_info(driver, href + "&pg=2", category_name, item_list)

            for item in item_list:

                # 商品詳細情報を取得する
                _get_item_detail_info(driver, item, category_name, result_list)

            CSVio.write_list_to_csv(csv_path, result_list)

            break

    finally:
        driver.quit()

def scraping_bybs4(category_name, url):
    """カテゴリURLを指定しての検索"""

    # csvに出力するリストを作成
    result_list = [["category", "ranking", "name", "price", "isprime", "stock", "delivery", "ASIN"]]
    item_list = []

    # 出力するCSVパス
    csv_path = CSV_ROOT_URL + category_name + ".csv"
    
    # ドライバを起動
    driver = Driver(False)
    
    try:
        # カテゴリ別商品一覧画面の情報を取得する
        _get_item_overview_info(driver, url, category_name, item_list)
        _get_item_overview_info(driver, url + "&pg=2", category_name, item_list)

        count = 0
        for item in item_list:

            count += 1
            if count >= 5:
                break

            # 商品詳細情報を取得する
            _get_item_detail_info(driver, item, category_name, result_list)

        CSVio.write_list_to_csv(csv_path, result_list)

    finally:
        driver.quit()

def get_category_dict(url, driver: Driver=None):
    """amazonの全カテゴリのカテゴリ名とURLを辞書形式で取得する"""
    # カテゴリ一覧画面に遷移する
    driver.get(url)

    # htmlを解析
    soup = BeautifulSoup(driver.page_source(), "lxml")

    # 全カテゴリのカテゴリ名： URLを保持する
    result = {}
    category_link_list = soup.select("#zg_browseRoot")[0].select("a")
    for elem in category_link_list:
        result[elem.text] = elem.get("href")
    return result

def get_category_list(url, driver: Driver=None):
    """amazonの全カテゴリのカテゴリ名とURLをリスト形式で取得する"""
    driver = Driver(True)

    try:
        # カテゴリ一覧画面に遷移する
        driver.get(url)

        # htmlを解析
        soup = BeautifulSoup(driver.page_source(), "lxml")

        # 全カテゴリのカテゴリ名： URLを保持する
        result = [["category_name", "category_url"]]
        category_link_list = soup.select("#zg_browseRoot")[0].select("a")
        for elem in category_link_list:
            result.append([elem.text, elem.get('href')])
        return result
    except Exception as err:
        logger.error(f"カテゴリ取得中にエラーが発生しました。error:{err}")
        return []
    finally:
        driver.quit()
        

def _get_item_overview_info(driver, href, category_name, item_list):
    """カテゴリ別商品一覧ページの情報を取得する"""
    # カテゴリ別商品一覧画面に遷移する
    driver.get(href)
    driver.wait_until_presence_of_all_elements_located()
    time.sleep(5)
    html = driver.page_source()
    soup = BeautifulSoup(html, "lxml")

    items_elems = soup.select(".zg-item-immersion")
    #zg-ordered-list > li:nth-child(3) > span > div > span > div.a-row > span > i

    # カテゴリ別商品一覧画面の情報を取得する
    for i, item_elem in enumerate(items_elems):

        try:
            item_dict = {}
            if i <= 10:
                print(item_elem.select("span > div > span > div.a-row > span"))
                # print(item_elem.select("span > div > span > div.a-row > span > i"))
            # ランキング
            item_dict['rank'] = item_elem.select(".zg-badge-text")[0].text.strip()
            
            # 商品名
            item_link = item_elem.select("span > div > span > a")[0]
            item_dict['item_name'] = item_link.text.strip()
            # 商品詳細リンク先
            item_dict['href'] = item_link.get("href")
            item_list.append(item_dict)
        except Exception as err:
            logger.info(f"カテゴリ:{category_name} > {i+1}個目のアイテム概要取得に失敗しました。error:{err}")


def _get_item_detail_info(driver, item, category, result_list):
    """商品詳細ページの情報を取得する"""
    # 商品詳細画面に遷移する
    url = item['href'] if "https://www.amazon.co.jp" in item['href'] else "https://www.amazon.co.jp/" + item['href']
    driver.get(url)
    driver.wait_until_presence_of_all_elements_located()
    time.sleep(1)
    html = driver.page_source()
    soup = BeautifulSoup(html, "lxml")

    # 商品名
    new_item_name = _get_item_from_selectors(soup, ["#btAsinTitle > span", "#productTitle"], category, item['item_name'], "item_name", "-")
    if new_item_name != "-":
        item['item_name'] = new_item_name
    # 商品価格
    price_selectors = ["#priceblock_ourprice", "#priceblock_dealprice", "#priceblock_saleprice", "#actualPriceValue > strong"]
    price = _get_item_from_selectors(soup, price_selectors, category, item['item_name'], "price", "-")

    # プライムか否か
    is_prime_elems = _get_item_from_selectors(soup, ["#priceBadging_feature_div > i > i", "#priceBadging_feature_div > i", "#priceBadging_feature_div"], category, item['item_name'], "is_prime", "its not prime")
    is_prime = 0 if is_prime_elems == "its not prime" else 1
    # 在庫
    availability = _get_item_from_selectors(soup, ["#availability > span"], category, item['item_name'], "availability", "在庫無し。")
    availability = 1 if "在庫あり。" == availability else 0
    # お届け日
    delivery = _get_item_from_selectors(soup, ["#ddmDeliveryMessage > b"], category, item['item_name'], "delivery", "-")
    # ASIN
    asin = _get_item_from_selectors(soup, ["#productDetails_detailBullets_sections1 > tbody > tr:nth-child(1) > td"], category, item['item_name'], "ASIN", "-")
    if asin == "-":
        asin_candidates = soup.select("#detailBullets_feature_div > ul > li")
        for asin_candidate in asin_candidates:
            if "ASIN" in asin_candidate.select("span > span:nth-child(1)")[0].text.strip():
                asin = asin_candidate.select("span > span:nth-child(2)")[0].text.strip()
                break
    result_list.append([category, item['rank'], item['item_name'], price, is_prime, availability, delivery, asin])


def _get_item_from_selectors(soup, selector_list, category, item_name, item_col, default):
    """存在するcssセレクタの値を返却する"""
    for selector in selector_list:
        item_list = soup.select(selector)
        if item_list:
            return item_list[0].text.strip()

    logger.info(f"カテゴリ:{category} > 商品名:{item_name} > カラム:{item_col}の取得に失敗しました。")
    return default

def _get_item_detail(func, category, item_name, item_col, default):
    """引数のカラムの値を取得する"""
    try:
        return func()
    except Exception as err:
        logger.info(f"カテゴリ:{category} > 商品名:{item_name} > カラム:{item_col}の取得に失敗しました。error:{err}")
        return default

if __name__ == "__main__":
    get_info()



