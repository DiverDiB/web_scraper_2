from urllib.parse import urlparse, urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict

import sys
import requests

# 1. Define the global structure blueprint ahead of time
class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

def normalize_url(url: str) -> str:
    url_parts = urlsplit(url)
    #print("\nurl_parts: ", url_parts)
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

def get_html(url: str) -> str:
    # Fetch with the required User-Agent header
    response = requests.get(url, headers={"User-Agent": "Bootcrawler/1.0"})

    # Raise an error if status code is 400 or greater
    response.raise_for_status()

    # Raise an error if content type is not text/html
    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        raise ValueError(f"Invalid content type: {content_type}")

    # Return the HTML text string
    return response.text

def crawl_page(base_url, current_url=None, page_data=None) -> dict[str, PageData]:
    # First call, set current_url to base_url
    if current_url is None:
        current_url = base_url

    # Initialize the page data dictionary if doesn't exist
    if page_data is None:
        page_data = {}

    # If not on same domain, return
    if not are_same_domain(base_url, current_url):
        return

    # Get normalized version of current url
    norm_current = normalize_url(current_url)

    # If already crawled, return
    if norm_current in page_data:
        return

    html = get_html(current_url)

    data = extract_page_data(html, current_url)

    page_data[norm_current] = data

    for link in data["outgoing_links"]:
        # Recursively crawl each link
        crawl_page(base_url, current_url=link, page_data=page_data)

    return page_data

def are_same_domain(base_url: str, current_url: str) -> bool:
    base_parsed = urlparse(base_url)
    current_parsed = urlparse(current_url)

    return base_parsed.netloc == current_parsed.netloc