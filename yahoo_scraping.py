import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv
#ChromeDriverのフルパス
CHROMEDRIVER = "chromedriver.exe"
#最大ページ数
MAX_PAGE = 2

def get_driver():
    
    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Chrome(CHROMEDRIVER, options=options)
    return driver

#オークションの検索
def get_auction_page(driver, url, word):
    
    driver.get(url)
    time.sleep(1) 
    elem_search = driver.find_element_by_xpath("//input[@placeholder='何をお探しですか？']")
    elem_search.send_keys(word)
    elem_search_click = driver.find_element_by_xpath("//input[@data-cl-params='_cl_vmodule:sbox;_cl_link:button;_cl_position:1;']")
    elem_search_click.click()

    time.sleep(1)

    cur_url = driver.current_url
    return cur_url

#開いているページのオークションURLをすべて抜き出す
def get_page_data(cur_url):
    req = requests.get(cur_url)
    soup = BeautifulSoup(req.text, "html.parser")

    auction_items = soup.find("ul", class_="Products__items").find_all("li")
    
    auction_urls = []
    for auction_item in auction_items:
        url_data = auction_item.find("h3", class_="Product__title")
        get_url = url_data.find("a", class_="Product__titleLink js-rapid-override js-browseHistory-add").get("href")
       
        auction_urls.append(get_url)
    return auction_urls

    #オークションの詳細データ
def auction_form_data(auction_url):
    req = requests.get(auction_url)
    soup = BeautifulSoup(req.text, "html.parser")
    
    title = soup.find("h1", class_="ProductTitle__text").text
    current_amount = soup.find("dd", class_="Price__value").text

    count_contents = soup.find("ul", class_="Count__counts").find_all("li")
    time_limit = count_contents[1].find(class_="Count__detail").text
    bid = count_contents[0].find(class_="Count__detail").text

    data_list = [title, current_amount, time_limit, bid, auction_url]

    return data_list

#オークションが条件に合うかどうかの判定
def data_judge(time_limit_t, bid_t, bid_num):

    count_result = False

    bid_t = int(bid_t[:-1])

    #残り時間が24時間未満の場合下の処理へ
    if "日" in time_limit_t:
        return count_result
    else:
        pass
    #入札数がbid_num以上の場合Trueを返す
    if bid_t >= bid_num:
        count_result = True
        return count_result
    else:
        return count_result
#次のページへ移る
def next_btn_click(driver):
    elem_next_btn = driver.find_element_by_xpath("//a[@data-cl-params='_cl_vmodule:pagination;_cl_link:next;_cl_position:1;']")
    elem_next_btn.click()

    time.sleep(3)



url = "https://auctions.yahoo.co.jp/"
word = "衣類"
bid_num = 1

HEADER = ["タイトル", "現在の金額", "残り時間", "入札数", "URL" ]


#ドライバーの取得
driver = get_driver()
#検索したページのURLを取得
cur_url = get_auction_page(driver, url, word)

flag = True
page_count = 0

with open(word+".csv", "w", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(HEADER)

while flag:

    page_count = page_count + 1

    #検索したページのオークションURLをすべて抜き出す
    auction_urls = get_page_data(cur_url)   


    for auction_url in auction_urls:

        data_list = auction_form_data(auction_url)
        time_limit_t= data_list[2]
        bid_t = data_list[3]

        judge_result = data_judge(time_limit_t, bid_t, bid_num)

        if judge_result == True:
            with open(word+".csv", "a", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(data_list)
                print("書き込み成功")

        else:

            continue
    
    if page_count == MAX_PAGE:
        break

    next_btn_click(driver)

    cur_url = driver.current_url

print("プログラム終了")

driver.quit()
    



    