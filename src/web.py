from .opt import solve
from .book import get_store_list, get_book_list

NUM_MAX_RESULT = 10

def processing(book_urls, min_quality):
    store_list = get_store_list()
    book_list = get_book_list(book_urls, store_list, min_quality)
    book_json = [None if book is None else book.to_dict() for book in book_list]
    result = solve(book_list, store_list)

    result_json = []
    for solution in result[:NUM_MAX_RESULT]:
        tmp = {"stores": [], "total_price":0}
        for item in solution:
            if item is None:
                continue
            item_dict = {
                "title":item.title,
                "quality":item.quality,
                "price":item.price,
                "link":item.link
            }
            find_flag = False
            for i, name in enumerate([dic["store_name"] for dic in tmp["stores"]]):
                if name == item.store_name:
                    tmp["stores"][i]["item_list"].append(item_dict)
                    tmp["stores"][i]["store_price"] += item.price
                    tmp["total_price"] += item.price
                    find_flag = True
                    break
            if not find_flag:
                store_dict = {
                    "store_name": item.store_name,
                    "item_list": [item_dict],
                    "store_price": item.price
                }
                tmp["stores"].append(store_dict)
                tmp["total_price"] += item.price
                
        result_json.append(tmp)

    result_json.sort(key=lambda x:x["total_price"])
    return {
        "search_result": book_json,
        "opt_result": result_json
    }, 200
