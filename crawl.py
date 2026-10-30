from urllib.parse import urlparse, urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict

import sys
import requests
import asyncio
import aiohttp

# 1. Define the global structure blueprint ahead of time
class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

class AsyncCrawler():
    def __init__(self, base_url, base_domain, max_concurrency=3, max_pages = 10):
        self.base_url = base_url
        self.base_domain = base_domain
        self.page_data = {}
        self.visited = set()
        self.max_concurrency = max_concurrency
        self.max_pages = max_pages
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session = None
        self.should_stop = False
        self.all_tasks = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        if self.should_stop:
            return False
        
        async with self.lock:
            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print(f"Reached maximum number of pages to crawl")
                return False
            if normalized_url in self.visited:
                return False
            self.visited.add(normalized_url)
            return True

    async def get_html(self, raw_url):
        try:
            async with self.session.get(raw_url) as response:
                # Check content-type header to ensure it's html
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    raise ValueError(f"Invalid content type: {content_type}")

                # Raise an error if status code is 400 or greater
                response.raise_for_status()

                # Return the HTML text string
                return await response.text()
        except Exception as e:
            print(f"Unexpected error fetching {raw_url}: {e}")
            return "" 

    async def crawl_page(self, current_url):
        # Check if should stop
        if self.should_stop:
            return
        # Same domain check
        parsed_url = urlparse(current_url)
        if parsed_url.netloc != self.base_domain:
            return

        # Normalize URL and check if already visited
        norm_url = normalize_url(current_url)
        if not await self.add_page_visit(norm_url):
            return

        # Limit concurrency with semaphore
        async with self.semaphore:
            print(f"Crawling: {current_url}")
            html = await self.get_html(current_url)
            if not html:
                return

            # Extract data 
            page_data = extract_page_data(html, self.base_url)
            #print(f"page_data: {page_data}")

        # Safely update shared page dictionary
        async with self.lock:
            self.page_data[norm_url] = page_data

        # Recursively crawl outgoing links
        tasks = []
        for link in page_data.get("outgoing_links", []):
            task = asyncio.create_task(self.crawl_page(link))
            self.all_tasks.add(task)
            tasks.append(task)

            task.add_done_callback(self.all_tasks.discard)

        if tasks:
            await asyncio.gather(*tasks)

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data

def normalize_url(url: str) -> str:
    url_parts = urlsplit(url)

    # Remove slash at end of path if present
    return url_parts.netloc + url_parts.path.rstrip('/')

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    # Look for h1 tag
    h_tag = soup.find('h1')

    # Extract text and look for actual content
    if isinstance(h_tag, Tag):
        heading_text = h_tag.get_text(strip=True)
        if heading_text:    # Ensure it's not an empty string
            return heading_text

    # Fall back to h2 if h1 not found
    h_tag = soup.find('h2')

    # Extract text and look for actual content
    if isinstance(h_tag, Tag):
        heading_text = h_tag.get_text(strip=True)
        if heading_text:    # Ensure it's not an empty string
            return heading_text

    # Return empty string if neither had valid text
    return ""

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    # First find main tag
    main_tag = soup.find('main')

    if isinstance(main_tag, Tag):
        # Look for paragraph (p) tag
        p_tag = main_tag.find('p')

        # Extract text and look for actual content
        if isinstance(p_tag, Tag):
            paragraph_text = p_tag.get_text(strip=True)
            if paragraph_text:  # Ensure it's not an empty string
                return paragraph_text

    # Return empty string if no valid text
    return ""

def get_first_paragraph_from_html_no_main(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    # Look for paragraph (p) tag
    p_tag = soup.find('p')

    # Extract text and look for actual content
    if isinstance(p_tag, Tag):
        paragraph_text = p_tag.get_text(strip=True)
        if paragraph_text:  # Ensure it's not an empty string
            return paragraph_text

    # Return empty string if no valid text
    return ""

def get_urls_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')
    urls = []

    # Find all a tags
    a_tag_list = soup.find_all('a')

    # Loop through list, convert to absolute URL and append to return list
    for url in a_tag_list:
        a_abs_url = urljoin(base_url, url.get('href'))
        urls.append(a_abs_url)
    return urls

def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')
    images = []

    # Find all img tags
    a_tag_list = soup.find_all('img')

    # Loop through list, convert to absolute URL and append to return list
    for image in a_tag_list:
        a_abs_url = urljoin(base_url, image.get('src'))
        images.append(a_abs_url)
    return images

def extract_page_data(html: str, page_url: str):
    h1_text = get_heading_from_html(html)
    p_text = get_first_paragraph_from_html_no_main(html)
    links = get_urls_from_html(html, page_url)
    images = get_images_from_html(html, page_url)

    return{
        "url":  page_url,
        "heading": h1_text,
        "first_paragraph": p_text,
        "outgoing_links": links,
        "image_urls": images,
    }

async def crawl_site_async(base_url, max_concurrency, max_pages):
    # Extract the domain to pass along with the URL
    parsed_url = urlparse(base_url)
    base_domain = parsed_url.netloc

    # This automatically triggers __aenter__(session opens) and __aexit__(session closes)
    async with AsyncCrawler(base_url, base_domain, max_concurrency, max_pages) as crawler:
        page_data = await crawler.crawl()
        return page_data
