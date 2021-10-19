import logging
from urllib import robotparser

import httpx
from bs4 import BeautifulSoup

from research.domain import Book

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(filename)s | %(levelname)s: %(message)s')


class PageParser:
    ok_status = 200

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
            logger.debug("Labirinth cache robots.txt doesn't permit to fetch this url;")
            return False
        logger.debug('Crawl delay {0}'.format(self.robots.crawl_delay(self.book_page_url)))
        return True

    def appropriate_status_code(self):
        code = self.response.status_code
        logger.debug(code)
        if code != self.ok_status:
            logger.debug(f"Page doesn't exist for book {self.book_id}. Status code {code}")
            return False
        return True

    def book_url(self):
        book_section = str(self.response.url).split('/')[-3]
        logger.debug(f'book section in url: {book_section}')
        return book_section == 'books'

    def find_book_id(self):
        return self.book_id

    def find_book_title(self):
        if not self.loaded:
            logger.debug('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        title_div = self.source.find('div', 'prodtitle')
        return title_div.h1.text

    def find_authors(self):
        if not self.loaded:
            logger.debug('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        authors_div = self.book_specs.find('div', 'authors')
        if authors_div:
            author = authors_div.a.text
        else:
            author = None
        return author

    def find_publisher(self):
        if not self.loaded:
            logger.debug('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        publisher = self.publisher_div.a.text
        if publisher == 'UNKNOWN':
            raise ValueError('Publisher == "UNKNOWN"')
        return publisher

    def find_year(self):
        if not self.loaded:
            logger.debug('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        return self.publisher_div.text.split()[-2]

    def find_isbn(self):
        if not self.loaded:
            logger.debug('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        isbn_div = self.book_specs.find('div', 'isbn')

        if isbn_div is not None:
            logger.debug(isbn_div.find_all())
            if isbn_div.find_all():
                logger.debug(isbn_div.text)
                isbn = isbn_div.text.split()[1]
                logger.debug(isbn)
            else:
                isbn = isbn_div.text.split()[-1]
        else:
            raise ValueError('No isbn!')
        if len(isbn) < 10:
            raise ValueError(f'Too short isbn "{isbn}"')
        return isbn

    def find_cover_image_url(self):
        if not self.loaded:
            logger.debug('Book page not loaded. Please .load() it first')
            return None
        if not self.book_page_exists:
            return None
        image_div = self.source.find('div', id='product-image')
        logger.debug(f'all: {image_div.find_all()};')
        if image_div.img.has_attr('data-src'):
            return image_div.img['data-src']
        raise ValueError('No image data-src in img tag')

    def find_annotation_text(self):
        if not self.loaded:
            logger.debug('Book page not loaded. Please .load() it first')
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
            return Book(
                self.find_book_id(),
                self.find_book_title(),
                self.find_authors(),
                self.find_publisher(),
                self.find_year(),
                self.find_isbn(),
                self.find_cover_image_url(),
                self.find_annotation_text(),
            )
        return None
