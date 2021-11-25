from .opt import solve, MINIMUM_PRICE, SHIPPING_FEE
from .book import get_store_list, get_book_list

NUM_MAX_RESULT = 3

store_list = None

def processing(book_urls, min_quality, online=True):
    global store_list
    
    if store_list is None:
        store_list = get_store_list()
    book_list = get_book_list(book_urls, min_quality, online)
    search_result = search_result_to_json(book_list)

    solutions = solve(book_list, store_list, online)
    solutions = solution_to_json(solutions, book_list, store_list, online)

    if online:
        solutions_const = solve(book_list, store_list, online, only_free_shipping=True)
        solutions_const = solution_to_json(solutions_const, book_list, store_list, online)
        
    return {
        "search_result": search_result,
        "solutions": solutions[:NUM_MAX_RESULT],
        "solutions_free_shipping": solutions_const[:NUM_MAX_RESULT] if online else None
    }

def search_result_to_json(book_list):
    search_result = []
    for book in book_list:
        if book is None:
            search_result.append(None)
        else:
            search_result.append({
                "title": book.title,
                "store_list": book.df["store_name"].tolist()
            })
    return search_result

def solution_to_json(solutions, book_list, store_list, online):
    opt_result = []
    for solution in solutions:
        solution_dict = {"stores": [], "total_price":0}
        for c in range(len(store_list)):
            store_name = store_list[c]
            store_dict = {}
            for r in range(len(book_list)):
                if solution[r][c] == 1:
                    book = book_list[r]
                    row = book.df[book.df["store_name"] == store_name]
                    item = row.iloc[0]
                    item_dict = {
                        "title":item["title"],
                        "quality":item["quality"],
                        "price":int(item["price"]),
                        "link":item["link"] if "link" in row.columns.values else None
                    }

                    find_store_flag = False
                    for i, name in enumerate([dic["store_name"] for dic in solution_dict["stores"]]):
                        if name == item.store_name:
                            solution_dict["stores"][i]["item_list"].append(item_dict)
                            solution_dict["stores"][i]["store_price"] += int(item.price)
                            solution_dict["total_price"] += int(item.price)
                            find_store_flag = True
                            break
                    if not find_store_flag:
                        store_dict = {
                            "store_name": item.store_name,
                            "item_list": [item_dict],
                            "store_price": int(item.price),
                            "discount": True
                        }
                        solution_dict["stores"].append(store_dict)
                        solution_dict["total_price"] += int(item.price)
                    
            if store_dict and store_dict["store_price"] < MINIMUM_PRICE:
                store_dict["store_price"] += SHIPPING_FEE
                store_dict["discount"] = False
                solution_dict["total_price"] += SHIPPING_FEE
            if not online:
                store_dict["discount"] = False

            solution_dict["stores"].sort(key=lambda x:-x["store_price"])
        opt_result.append(solution_dict)
    
    opt_result.sort(key=lambda x:x["total_price"])
    
    return opt_result
    
def print_result(result, online):
    print("Optimization Results... ")
    if len(result["solutions"]) == 0:
        print("No Results")
        print('END')
        return    
    
    if online:
        print(f"*** Solutions without free shipping constraint ***")
    for idx, solution_dict in enumerate(result["solutions"]):
        print(f"*** Solution {idx+1}: {solution_dict['total_price']}원 ***")
        
        for store_dict in solution_dict["stores"]:
            print(f"{' '*4}{store_dict['store_name']}: {store_dict['store_price']}원", end='')
            print(f"{' 배송비 할인' if store_dict['discount'] else ''}")
            for item in store_dict["item_list"]:
                print(f"{' '*8}'{item['title']}' {item['quality']} {item['price']}원 {item['link'] if item['link'] is not None else ''}")     
            print()
        print()
    
    if online:
        print(f"*** Solutions with free shipping constraint ***")
        for idx, solution_dict in enumerate(result["solutions_free_shipping"]):
            print(f"*** Solution {idx+1}: {solution_dict['total_price']}원 ***")
            
            for store_dict in solution_dict["stores"]:
                print(f"{' '*4}{store_dict['store_name']}: {store_dict['store_price']}원", end='')
                print(f"{' 배송비 할인' if store_dict['discount'] else ''}")
                for item in store_dict["item_list"]:
                    print(f"{' '*8}'{item['title']}' {item['quality']} {item['price']}원 {item['link'] if item['link'] is not None else ''}")     
                print()
            print()
    
    print('END')


    