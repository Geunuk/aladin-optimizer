import argparse

from src.opt import solve
from src.book import get_store_list, get_book_list

def print_result(result):
    print('-'*20+" Optimization Results "+'-'*19)
    if len(result) == 0:
        print("No Results")
    else:
        for idx, solution in enumerate(result):
            print("-"*25 +  f" Solution {idx+1} " + "-"*24)
            solution.sort(key=lambda x:str(x))
            for elm in solution:
                print(elm)
            print()
    print('-'*61)


    
def main():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('book_urls', nargs='*', help="ex) https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=16294019")
    parser.add_argument('--min_quality', '-q', type=str, default="상", choices=["하", "중", "상", "최상"])
    args = parser.parse_args()
    
    store_list = get_store_list()
    book_list = get_book_list(args.book_urls, store_list, args.min_quality)
    result = solve(book_list, store_list)
    print_result(result)
    
if __name__ == "__main__":
    main()
