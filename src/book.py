import re
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

import requests
from bs4 import BeautifulSoup

used_book_main_url = "https://www.aladin.co.kr/usedstore/wgate.aspx"
quality_numbers = {'하':0, '중':1, '상':2, '최상':3}

class Item():
    def __init__(self, title, link, quality, price, store_name):
        self.title = title
        self.link = link
        self.quality = quality
        self.price = price
        self.store_name = store_name
    
    def __str__(self):
        return f"{self.store_name} {self.title} {self.quality} {self.price} {self.link}"

class Book():
    def __init__(self, title, item_list):
        self.title = title
        self.item_list = item_list

    def __str__(self):
        return '\n'.join(map(str, self.item_list))

    def find_item(self, store_name):
        for item in self.item_list:
            if item.store_name == store_name:
                return item
        return None
        
    def to_dict(self):
        return {
            "title": self.title,
            "store_list": [item.store_name for item in self.item_list]
        }

def get_store_list():
    print(f"Start crawling stores...")
    html = requests.get(used_book_main_url).text
    soup = BeautifulSoup(html, "lxml")

    store_list = []
    for x in (soup.find("table", {"class": "gatetopwrap_table"}).find_all("a")):
        parsed_url = urlparse(x["href"])
        if "offcode" in parse_qs(parsed_url.query):
            store_name = x.text.replace(" ", "")
            store_list.append(store_name)
    print(f"Find {len(store_list)} stores...")
    return store_list

def book_url_to_used_book_url(book_url):
    parsed_url = urlparse(book_url)
    item_id = parse_qs(parsed_url.query)["ItemId"][0]
    
    used_book_url = urlparse(
            "https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx")
    used_book_url = used_book_url._replace(
                            query=urlencode(
                                {"ItemId":item_id,
                                 "TabType": 3 # Only aladin offline seller
                                 }))
    used_book_url = urlunparse(used_book_url)
    return used_book_url

def search_book(book_url, min_quality, store_list):
    used_book_url = book_url_to_used_book_url(book_url)
    
    html = requests.get(used_book_url).text
    soup = BeautifulSoup(html, "lxml")

    book_title = soup.find('a', attrs={"class":'Ere_bo_title'}).text
    link_search_results = soup.find_all('td', attrs={'class':"sell_tableCF1"})
    links = []
    for l in link_search_results:
        links.append(l.a["href"])

    item_list = []
    price_pat = re.compile('[0-9,]*원')
    store_pat = re.compile('중고매장.*점$')
    search_results = soup.find_all('td', attrs={'class':"sell_tableCF3"})
    store_name_to_price = {}
    for i in range(0, len(search_results), 4):
        link = links[i//4]

        quality = search_results[i].text.strip()
        if quality_numbers[quality] < quality_numbers[min_quality]:
            continue

        price_text= search_results[i+1].text.strip()
        price = int(re.match(price_pat, price_text).group().replace(',', "").replace("원", ""))
        
        store_name = search_results[i+2].text.strip()
        store_name = re.search(store_pat, store_name).group()[4:]
        store_name = store_name.replace(" ", "")
        store_name = store_name.replace(".", "")
        assert store_name in store_list

        if store_name not in store_name_to_price or store_name_to_price[store_name] > price:
            store_name_to_price[store_name] = price
            item_list.append(Item(book_title, link, quality, price, store_name))
    
    return Book(book_title, item_list)

def get_book_list(book_urls, store_list, min_quality):
    print(f"Start crawling with minimum quality '{min_quality}'...")
    book_list = []
    for book_url in book_urls:
        try:
            book = search_book(book_url, min_quality, store_list)
        except:
            print(f"Cannot access '{book_url}'...")
            book_list.append(None)
        else:
            print(f"Found {len(book.item_list)} items of '{book.title}'...")
            book_list.append(book)
    print("End crawling...")

    return book_list