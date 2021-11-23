from .opt import solve, MINIMUM_PRICE, DELIVERY_FEE
from .book import get_store_list, get_book_list

NUM_MAX_RESULT = 10

def processing(book_urls, min_quality):
    store_list = get_store_list()
    book_list = get_book_list(book_urls, store_list, min_quality)
    book_json = [None if book is None else book.to_dict() for book in book_list]
    solutions = solve(book_list, store_list)

    opt_result = []
    for solution in solutions:
        solution_dict = {"stores": [], "total_price":0}
        for c in range(len(store_list)):
            store_name = store_list[c]
            store_dict = {}
            for r in range(len(book_list)):
                if solution[r][c] == 1:
                    item = book_list[r].find_item(store_name)
                    item_dict = {
                        "title":item.title,
                        "quality":item.quality,
                        "price":item.price,
                        "link":item.link
                    }

                    find_store_flag = False
                    for i, name in enumerate([dic["store_name"] for dic in solution_dict["stores"]]):
                        if name == item.store_name:
                            solution_dict["stores"][i]["item_list"].append(item_dict)
                            solution_dict["stores"][i]["store_price"] += item.price
                            solution_dict["total_price"] += item.price
                            find_store_flag = True
                            break
                    if not find_store_flag:
                        store_dict = {
                            "store_name": item.store_name,
                            "item_list": [item_dict],
                            "store_price": item.price,
                            "discount": True
                        }
                        solution_dict["stores"].append(store_dict)
                        solution_dict["total_price"] += item.price
                    
            if store_dict and store_dict["store_price"] < MINIMUM_PRICE:
                store_dict["store_price"] += DELIVERY_FEE
                store_dict["discount"] = False
                solution_dict["total_price"] += DELIVERY_FEE
            solution_dict["stores"].sort(key=lambda x:-x["store_price"])
        opt_result.append(solution_dict)
    
    opt_result.sort(key=lambda x:x["total_price"])
    return {
        "search_result": book_json,
        "opt_result": opt_result[:NUM_MAX_RESULT]
    }

def print_result(result):
    print("Optimization Results... ")
    if len(result) == 0:
        print("No Results")
    else:
        for idx, solution_dict in enumerate(result["opt_result"]):
            print(f"*** Solution {idx+1}: {solution_dict['total_price']}원 ***")
            
            for store_dict in solution_dict["stores"]:
                print(f"{' '*4}{store_dict['store_name']}: {store_dict['store_price']}원", end='')
                print(f"{' 배송비 할인' if store_dict['discount'] else ''}")
                for item in store_dict["item_list"]:
                    print(f"{' '*8}'{item['title']}' {item['quality']} {item['price']}원 {item['link']}")     
                print()
            print()
    print('END')


    