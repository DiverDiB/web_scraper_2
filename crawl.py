from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag

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

def main():
    input_url = "https://www.boot.dev/blog/path/"
    normalize_url(input_url)
    return

if __name__ == "__main__":
    main()
