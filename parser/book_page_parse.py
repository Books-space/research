import logging
from dataclasses import dataclass
from urllib import robotparser
from bs4 import BeautifulSoup
import httpx


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(filename)s | %(levelname)s: %(message)s')


@dataclass
class Book:
    title: str
    author: str
    publisher: str
    year: int
    isbn: str
    cover_image_url: str
    annotation: str


class SingleBookPageParser:
    def __init__(self, book_id, base_url, robots_txt):
        self.base_url = base_url
        self.book_id = book_id
        self.robots = robotparser.RobotFileParser()
        self.robots.set_url(robots_txt)
        self.robots.read()
        self.loaded = False

    def load(self):
        self.book_page_url = self.base_url.format(self.book_id)
        logger.debug(self.book_page_url)
        self.response = httpx.get(self.book_page_url)

        self.loaded = True

        self.book_page_exists = True

        if not self.appropriate_status_code():
            self.book_page_exists = False
            return

        if not self.robots_permit():
            self.book_page_exists = False
            return

        if not self.book_url():
            self.book_page_exists = False
            return

        self.source = BeautifulSoup(self.response.text, 'lxml')
        # Find book specs block
        self.book_specs = self.source.find('div', 'product-description')
        self.publisher_div = self.book_specs.find('div', 'publisher')

    def robots_permit(self):
        if not self.robots.can_fetch('*', self.book_page_url):
            logger.debug('Labirinth cache robots.txt doesn\'t permit to fetch this url;')
            return False
        logger.debug('Crawl delay {}'.format(self.robots.crawl_delay(self.book_page_url)))
        return True

    def appropriate_status_code(self):
        code = self.response.status_code
        logger.info(code)
        if code != 200:
            logger.debug(f'Page doesn\'t exist for book {self.book_id}. Status code {code}')
            return False
        return True

    def book_url(self):
        book_section = str(self.response.url).split('/')[-3]
        logger.debug(f'book section in url: {book_section}')
        return book_section == 'books'

    def find_book_title(self):
        if not self.loaded:
            print('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        title_div = self.source.find('div', 'prodtitle')
        book_title = title_div.h1.text
        return book_title

    def find_authors(self):
        if not self.loaded:
            print('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        authors_div = self.book_specs.find('div', 'authors')
        if authors_div:
            author = authors_div.a.text
        else:
            author = '-'
        return author

    def find_publisher(self):
        if not self.loaded:
            print('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        publisher = self.publisher_div.a.text
        return publisher

    def find_year(self):
        if not self.loaded:
            print('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        year = self.publisher_div.text.split()[-2]
        return year

    def find_isbn(self):
        if not self.loaded:
            print('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        isbn_div = self.book_specs.find('div', 'isbn')

        if isbn_div is not None:
            isbn = isbn_div.text.split()[-1]
        else:
            isbn = '-'
        return isbn

    def find_cover_image_url(self):
        if not self.loaded:
            print('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        image_div = self.source.find('div', id='product-image')
        src_key = ''
        image_url = 'no_path'
        if image_div.img.has_attr('src'):
            src_key = 'src'
        elif image_div.img.has_attr('data-src'):
            src_key = 'data_src'
        if src_key:
            image_url = image_div.img[src_key]
        return image_url

    def find_annotation_text(self):
        if not self.loaded:
            print('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        about_div = self.source.find('div', id='product-about')
        if about_div.find('p'):
            annotation = about_div.p.text
        else:
            annotation = about_div.text
        return annotation

    def return_result(self):
        if self.loaded and self.book_page_exists:
            return Book(self.find_book_title(),
                        self.find_authors(),
                        self.find_publisher(),
                        self.find_year(),
                        self.find_isbn(),
                        self.find_cover_image_url(),
                        self.find_annotation_text())
        return None
