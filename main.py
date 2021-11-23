import argparse

from src.book import get_store_list, get_book_list
from src.pipeline import processing, print_result

def main():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('book_urls', nargs='*', help="ex) https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=16294019")
    parser.add_argument('--min_quality', '-q', type=str, default="상", choices=["하", "중", "상", "최상"])
    args = parser.parse_args()

    result = processing(args.book_urls, args.min_quality)
    print_result(result)
    
if __name__ == "__main__":
    main()