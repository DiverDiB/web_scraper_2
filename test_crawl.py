import unittest
from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html

class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_url_without_netloc(self):
        input_url = "//www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_url_with_query(self):
        input_url = "https://www.boot.dev/blog/path?query=python"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_url_with__slash(self):
        input_url = "https://www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_url_with_only_netloc(self):
        input_url = "//www.boot.dev"
        actual = normalize_url(input_url)
        expected = "www.boot.dev"
        self.assertEqual(actual, expected)

    def test_url_all_parts(self):
        input_url = "http://www.boot.dev/blog/path?query=code&category=python&sort=num_devs"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_get_h1_from_html_basic(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_h2_from_html_basic(self):
        input_body = "<html><body><h1></h1><h2>Secondary Heading</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Secondary Heading"
        self.assertEqual(actual, expected)

    def test_get_h1_h2_present(self):
        input_body = "<html><body><h1>Test Title</h1><h2>Secondary Heading</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
         <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_main(self):
        input_body = """<html><body>
         <p>Outside paragraph.</p>
         <p>Main paragraph.</p>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_multiple(self):
        input_body = """<html><body>
         <p>Outside paragraph 1></p>
            <main>
                <p>Main paragraph 1</p>
                <p>Main paragraph 2</p>
            </main>
         <p>Outside paragraph 2></p>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph 1"
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_multiple_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <a href="https://crawler-test.com"><span>Boot.dev</span></a>
            <a href="https://another-test.com"><span>BootAgain.dev></a>
        </body></html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com", "https://another-test.com"]
        self.assertEqual(actual, expected)

def test_get_multiple_urls_from_html_both(self):
    input_url = "https://crawler-test.com"
    input_body = '''
        <html>
            <body>
                <a href="/path/to/page">Relative Link</a>
                <a href="https://crawler-test.com/absolute">Absolute Link</a>
            </body>
        </html>
        '''
    actual = get_urls_from_html(input_body, input_url)
    expected = [
        "https://crawler-test.com/path/to/page",
        "https://crawler-test.com/absolute"
    ]
    self.assertEqual(actual, expected)

def test_get_images_from_html_relative(self):
    input_url = "https://crawler-test.com"
    input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
    actual = get_images_from_html(input_body, input_url)
    expected = ["https://crawler-test.com/logo.png"]
    self.assertEqual(actual, expected)

def test_get_multiple_images_from_html_both(self):
    input_url = "https://crawler-test.com"
    input_body = """<html><body>
        <img src="/img/path/logo.png" alt="Logo">
        <img srce="https://crawler-test.com/img/path/logo2.png">
    </body></html>"""
    actual = get_images_from_html(input_body, input_url)
    expected = [
        "https://crawler-test.com/logo.png",
        "https://crawler-test.com/img/path/logo2.png"
    ]
    self.assertEqual(actual, expected)

def test_no_images(self):
    input_url = "https://crawler-test.com"
    input_body = '''
        <html>
            <body>
                <a href="/path/to/page">Relative Link</a>
                <a href="https://crawler-test.com/absolute">Absolute Link</a>
            </body>
        </html>
        '''
    actual = get_images_from_html(input_body, input_url)
    expected = []
    self.assertEqual(actual, expected)
if __name__ == "__main__":
    unittest.main()