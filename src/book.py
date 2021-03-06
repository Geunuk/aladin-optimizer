import re
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

import requests
import pandas as pd
from bs4 import BeautifulSoup

TTB_KEY = "ttbgeunukj0838001"

used_book_main_url = "https://www.aladin.co.kr/usedstore/wgate.aspx"
quality_numbers = {'하':0, '중':1, '상':2, '최상':3}

class Item():
    def __init__(self, title, quality, price, store_name, link=None):
        self.title = title
        self.link = link
        self.quality = quality
        self.price = price
        self.store_name = store_name
        self.off_code = off_code
    
    def __str__(self):
        return f"{self.store_name} {self.title} {self.quality} {self.price} {self.link}"

class Book():
    def __init__(self, title, df):
        self.title = title
        self.df = df

def get_total_store_list():
    print(f"Start crawling stores...")
    res = requests.get(used_book_main_url)
    assert res.status_code == 200
    html = res.text
    soup = BeautifulSoup(html, "lxml")

    store_list = ["알라딘 직접 배송"]
    for a_tag in soup.select("table.gatetopwrap_table a"):
        store_name = a_tag.text.replace(" ", "")
        store_list.append(store_name)

    print(f"Find {len(store_list)} stores...")
    return store_list

def get_quality_list(search_result):
    return [search_result[i].text.strip() for i in range(0, len(search_result), 4)]

def get_price_list(search_result):
    price_pat = re.compile('[0-9,]*원')
    
    func = lambda price_text: int(re.match(price_pat, price_text).group().replace(',', "").replace("원", ""))
    result = [search_result[i+1].text.strip() for i in range(0, len(search_result), 4)]
    return list(map(func, result))
    
def get_selling_store_list(search_result, aladin_direct):
    result = [search_result[i+2].text.strip() for i in range(0, len(search_result), 4)]
    if aladin_direct:
        return result
    else:
        store_pat = re.compile('중고매장.*점$')
        func = lambda store_name: re.search(store_pat, store_name).group()[4:].replace(" ", "").replace(".", "")
        return list(map(func, result))

def book_url_to_used_book_url(book_url, aladin_direct):
    parsed_url = urlparse(book_url)
    try:
        item_id = parse_qs(parsed_url.query)["ItemId"][0]
    except KeyError:
        return None

    used_book_url = urlparse(
            "https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx")
    used_book_url = used_book_url._replace(
                            query=urlencode(
                                {"ItemId":item_id,
                                 "TabType": 2 if aladin_direct else 3
                                 }))
    used_book_url = urlunparse(used_book_url)
    return used_book_url

def get_info(book_url, aladin_direct):
    used_book_url = book_url_to_used_book_url(book_url, aladin_direct)
    if used_book_url is None:
        return None

    res = requests.get(used_book_url)
    if res.status_code != 200:
        return None
    
    html = res.text
    soup = BeautifulSoup(html, "lxml")
    search_result = soup.find_all('td', attrs={'class':"sell_tableCF3"})
    
    book_title = soup.find('a', attrs={"class":'Ere_bo_title'}).text
    quality_list = get_quality_list(search_result)
    price_list = get_price_list(search_result)
    store_list = get_selling_store_list(search_result, aladin_direct)
    link_list = [tag["href"] for tag in soup.select("td.sell_tableCF1 > a")]
    assert len(quality_list) == len(price_list) == len(store_list) == len(link_list)

    data = {"title": book_title,
            "quality": quality_list,
            "quality_num": [quality_numbers[q] for q in quality_list],
            "price": price_list,
            "store_name": store_list,
            "link": link_list}
    return data

def search_book_online(book_url):
    info = get_info(book_url, False)
    info_direct = get_info(book_url, True)
    if info is None or info_direct is None:
        return None
    assert info["title"] == info_direct["title"]
    
    book_title = info["title"]
    total_data = {"title": [book_title]*(len(info["quality"])+len(info_direct["quality"])),
                  "quality": info["quality"] + info_direct["quality"],
                  "quality_num": info["quality_num"] + info_direct["quality_num"],
                  "price": info["price"] + info_direct["price"],
                  "store_name": info["store_name"] + info_direct["store_name"],
                  "link": info["link"] + info_direct["link"]}
    return Book(book_title, pd.DataFrame(total_data))

def search_book_offline(book_url):
    parsed_url = urlparse(book_url)
    try:
        item_id = parse_qs(parsed_url.query)["ItemId"][0]
    except KeyError:
        return None
    url = "http://www.aladin.co.kr/ttb/api/ItemOffStoreList.aspx"
    params = {"TTBKey":TTB_KEY, "ItemIdType":"ItemId", "ItemId":item_id, "output":"js"}
    res = requests.get(url, params=params)
    if res.status_code != 200:
        return None
    data = res.json()
    empty_df = pd.DataFrame({'title': pd.Series(dtype='str'),
                   'quality': pd.Series(dtype='str'),
                   'quality_num': pd.Series(dtype='int'),
                   'price': pd.Series(dtype='int'),
                   "store_name": pd.Series(dtype='str')})
    df_list = [empty_df]
    for store_dict in data["itemOffStoreList"]:
        link = store_dict["link"].replace("amp;", '')
        off_code = parse_qs(link)["OffCode"][0] # TODO:remove
        df = crawl_store_page(link)
        df_list.append(df)
    # TODO: 자료 없어도 책이름 뽑기
    book_df = pd.concat(df_list, ignore_index=True)
    
    if len(book_df) == 0:
        book_title = item_id_to_title(item_id)
    else:
        book_title = book_df.iloc[0]["title"]    
    return Book(book_title, book_df)

def crawl_store_page(link):
    res = requests.get(link)
    if res.status_code != 200:
        return pd.DataFrame({'title': pd.Series(dtype='str'),
                   'quality': pd.Series(dtype='str'),
                   'quality_num': pd.Series(dtype='int'),
                   'price': pd.Series(dtype='int'),
                   "store_name": pd.Series(dtype='str')})
    html = res.text
    soup = BeautifulSoup(html, "lxml")
    
    store_name = soup.select_one(".text1 > a").text
    store_name = store_name.replace("알라딘 중고서점", "").strip()
    
    title_list = []
    price_list = []
    quality_list = []
    for book_tag in soup.select(".ss_book_box"):
        book_title = book_tag.select_one("div.ss_book_list ul li:nth-of-type(1) span").text
        book_title = book_title.replace("[중고]", "").strip()
        title_list.append(book_title)

        price = book_tag.select_one(".ss_p2").text.strip()
        price = int(price.replace(',', "").replace("원", ""))
        price_list.append(price)

        quality = book_tag.select_one(".us_f_bob").text.strip()
        quality_list.append(quality)

    data = {"title": title_list,
            "quality": quality_list,
            "quality_num": [quality_numbers[q] for q in quality_list],
            "price": price_list,
            "store_name": [store_name] * len(title_list)} 
    return pd.DataFrame(data)

def get_book_list(book_urls, min_quality, online):
    print(f"Start crawling with minimum quality '{min_quality}'...")
    book_list = []
    for book_url in book_urls:
        if online:
            book = search_book_online(book_url)
        else:
            book = search_book_offline(book_url)
        
        if book is None:
            print(f"Cannot access '{book_url}'...")
            book_list.append(None)
        else:
            #title = book_df.iloc[0]['title']
            book.df = book.df[book.df['quality_num'] >= quality_numbers[min_quality]]
            book.df = filtering(book.df, min_quality)
            print(f"Found {len(book.df)} items of '{book.title}'...")
            book_list.append(book)
            
    print("End crawling...")

    return book_list

def item_id_to_title(item_id):
    url = " http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
    params = {"TTBKey":TTB_KEY, "ItemIdType":"ItemId", "ItemId":item_id, "output":"js"}
    params = {"TTBKey":TTB_KEY, "ItemIdType":"ItemId", "ItemId":item_id, "output":"xml"}
    res = requests.get(url, params=params)
    if res.status_code != 200:
        return ''
    
    soup = BeautifulSoup(res.text, 'lxml')
    title = soup.select_one('object > item > title').text.strip()
    sub_title = soup.select_one('subTitle').text.strip()
    title = title.replace(" - " + sub_title, "").strip()
    return title
    
def filtering(book_df, min_quality):
    if len(book_df) != 0:
        return book_df.loc[book_df.groupby("store_name")["price"].idxmin()]
    else:
        return book_df