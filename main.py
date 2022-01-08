import argparse

from src.pipeline import processing, print_result

def main():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('book_urls', nargs='*', help="ex) https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=16294019")
    parser.add_argument('--min_quality', '-q', type=str, default="상", choices=["하", "중", "상", "최상"])
    parser.add_argument('--not_online', '-n', action="store_true", help="Use offline service. Not online service(우주점)")
    args = parser.parse_args()

    result = processing(args.book_urls, args.min_quality, not args.not_online )
    print_result(result, not args.not_online )
    
if __name__ == "__main__":
    main()