import argparse

from opt import solve

def print_result(result):
    print('-'*20+" Optimization Result "+'-'*20)
    for idx, l in enumerate(result):
        print("-"*25 +  f" Solution {idx+1} " + "-"*24)
        l.sort(key=lambda x:repr(x))
        for elm in l:
            print(elm)
        print()
    print('-'*61)

def main():
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('book_urls', nargs='*')
    args = parser.parse_args()
    
    result = solve(args.book_urls)
    print_result(result)

if __name__ == "__main__":
    main()
