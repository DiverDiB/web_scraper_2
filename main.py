import sys
import asyncio
from crawl import crawl_site_async

async def main():        
    if len(sys.argv) > 4:
        print("too many arguments provided")
        sys.exit(1)

    
        
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://boot.dev"
    max_concurrency = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    print(f"Beginning crawl of {base_url} with max concurrency of {max_concurrency} and max pages of {max_pages}")
    
    # Await the crawler
    page_data = await crawl_site_async(base_url, max_concurrency, max_pages)

    print(f"\nCrawl complete! Found {len(page_data)} pages.")

    # Iterate over the page data 
    for data in page_data.values():
        print(f" - {data['url']} ({data.get('heading', 'No heading')})")

if __name__ == "__main__":
    asyncio.run(main())