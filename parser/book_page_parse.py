from urllib import robotparser
from dataclasses import dataclass
from bs4 import BeautifulSoup
import httpx


BOOK_BASE_URL = 'https://www.labirint.ru/books/81249{}/'
LABIRINT_ROBOTS = 'https://www.labirint.ru/robots.txt'
LABIRINT_ROBOT_PARSER = robotparser.RobotFileParser()
LABIRINT_ROBOT_PARSER.set_url(LABIRINT_ROBOTS)
LABIRINT_ROBOT_PARSER.read()


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

    def robots_permit(self, url):
        if not LABIRINT_ROBOT_PARSER.can_fetch('*', url):
            print('Labirinth cache robots.txt doesn\'t permit to fetch this url;')
            return False
        print('Crawl delay {}'.format(LABIRINT_ROBOT_PARSER.crawl_delay(url)))
        return True

    def __init__(self, book_number):
        book_page_url = BOOK_BASE_URL.format(book_number)
        print(book_page_url)
        if not self.robots_permit(book_page_url):
            self.book_page_exists = False
            return

        self.book_number = book_number
        self.book_page_exists = True
        request_result = httpx.get(book_page_url)
        code = request_result.status_code
        if code < 200 or code > 299:
            print(f'\n-----\nPage doesn\'t exist for book {book_number}. Status code {code}')
            self.book_page_exists = False
            return

        self.source = BeautifulSoup(request_result.text, 'lxml')
        # Find book specs block
        self.book_specs = self.source.find('div', 'product-description')
        self.publisher_div = self.book_specs.find('div', 'publisher')

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
    for i in range(10):
        print(i)
        book_parser = SingleBookPageParser(i)
        print(book_parser.return_result().__repr__())
