import logging
from urllib import robotparser
from time import sleep
from random import uniform
from dataclasses import dataclass
from bs4 import BeautifulSoup
import httpx


BOOK_BASE_URL = 'https://www.labirint.ru/books/81249{}/'
LABIRINT_ROBOTS_TXT = 'https://www.labirint.ru/robots.txt'

logger = logging.getLogger('book_page_parser')

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
    def __init__(self, book_number):
        self.book_number = book_number
        self.robots = robotparser.RobotFileParser()
        self.robots.set_url(LABIRINT_ROBOTS_TXT)
        self.robots.read()
        self.book_page_url = BOOK_BASE_URL.format(book_number)
        logger.debug(self.book_page_url)
        self.book_number = book_number
        self.book_page_exists = True
        self.request_result = httpx.get(self.book_page_url)

        if (self.robots_dont_permit() or self.inappropriate_status_code() or self.not_book_url()):
            self.book_page_exists = False
            return

        self.source = BeautifulSoup(self.request_result.text, 'lxml')
        # Find book specs block
        self.book_specs = self.source.find('div', 'product-description')
        self.publisher_div = self.book_specs.find('div', 'publisher')

    def robots_dont_permit(self):
        if not self.robots.can_fetch('*', self.book_page_url):
            logger.debug('Labirinth cache robots.txt doesn\'t permit to fetch this url;')
            return True
        redirection_url = self.request_result.url
        if redirection_url != self.book_page_url:
            logger.debug(f'Redirected to:\n{redirection_url};')
            if not self.robots.can_fetch('*', self.book_page_url):
                logger.debug('Labirinth cache robots.txt doesn\'t permit to fetch this url;')
                return True
        logger.debug('Crawl delay {}'.format(self.robots.crawl_delay(self.book_page_url)))
        return False

    def inappropriate_status_code(self):
        code = self.request_result.status_code
        if code < 200 or code > 299:
            logger.debug(f'\n-----\nPage doesn\'t exist for book {self.book_number}. Status code {code}')
            return True
        return False

    def not_book_url(self):
        book_section = str(self.request_result.url).split('/')[-3]
        logger.debug(f'book section in url: {book_section}')
        return book_section != 'books'

    def find_book_title(self):
        if not self.book_page_exists:
            return None
        title_div = self.source.find('div', 'prodtitle')
        book_title = title_div.h1.text
        return book_title

    def find_authors(self):
        if not self.book_page_exists:
            return None
        authors_div = self.book_specs.find('div', 'authors')
        if authors_div:
            author = authors_div.a.text
        else:
            author = '-'
        return author

    def find_publisher(self):
        if not self.book_page_exists:
            return None
        publisher = self.publisher_div.a.text
        return publisher

    def find_year(self):
        if not self.book_page_exists:
            return None
        year = self.publisher_div.text.split()[-2]
        return year

    def find_isbn(self):
        if not self.book_page_exists:
            return None
        isbn_div = self.book_specs.find('div', 'isbn')

        if isbn_div is not None:
            isbn = isbn_div.text.split()[-1]
        else:
            isbn = '-'
        return isbn

    def find_cover_image_url(self):
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
        if not self.book_page_exists:
            return None
        about_div = self.source.find('div', id='product-about')
        annotation = about_div.p.text
        return annotation

    def return_result(self):
        if self.book_page_exists:
            return Book(self.find_book_title(),
                        self.find_authors(),
                        self.find_publisher(),
                        self.find_year(),
                        self.find_isbn(),
                        self.find_cover_image_url(),
                        self.find_annotation_text())
        return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    for i in range(10):
        if i > 0:
            pause_period = uniform(1.0, 3.0)
            logger.debug(f'wait for:{pause_period} sec.')
            logger.debug(pause_period)
            sleep(pause_period)
        logger.debug(i)
        book_parser = SingleBookPageParser(i)
        logger.debug(book_parser.return_result().__repr__())
