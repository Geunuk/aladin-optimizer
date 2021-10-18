import argparse

from opt import solve

def print_result(result):
    print('-'*20+" Optimization Results "+'-'*19)
    if len(result) == 0:
        print("No Results")
    else:
        for idx, l in enumerate(result):
            print("-"*25 +  f" Solution {idx+1} " + "-"*24)
            l.sort(key=lambda x:str(x))
            for elm in l:
                print(elm)
            print()
    print('-'*61)

def main():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('book_urls', nargs='*', help="ex) https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=16294019")
    parser.add_argument('--quality', '-q', type=str, default="상", choices=["하", "중", "상", "최상"])
    args = parser.parse_args()
    
    result = solve(args.book_urls, args.quality)
    print_result(result)

if __name__ == "__main__":
    main()
