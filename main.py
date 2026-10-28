import sys
from crawl import crawl_page

def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
        
    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
        
    base_url = sys.argv[1]
    print(f"starting crawl of: {base_url}")
    
    # Later, you'll call your crawler function here!
    result = crawl_page(base_url)
    print(f"result:\n{result}")

if __name__ == "__main__":
    main()