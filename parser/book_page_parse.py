from bs4 import BeautifulSoup
import httpx
import json


GOOGLE_CACHE_PATH = 'http://webcache.googleusercontent.com/search?q=cache:'
BOOK_BASE_URL = 'https://www.labirint.ru/books/81239{}/'


class ParseSingleBookPage:
    def __init__(self, book_number):
        self.book_page_exists = True
        request_result = httpx.get(''.join((GOOGLE_CACHE_PATH, BOOK_BASE_URL.format(book_number))))
        code = request_result.status_code
        if code < 200 or code > 299:
            print(f'\n-----\nPage doesn\'t exist for book {book_number}. Status code {code}')
            self.book_page_exists = False
            return

        self.source = BeautifulSoup(request_result.text, 'lxml')
        # Find book specs block
        self.book_specs = self.source.find('div', 'product-description')
        
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
        publisher_div = self.book_specs.find('div', 'publisher')
        publisher = publisher_div.a.text
        return publisher

    def find_year(self):
        if not self.book_page_exists:
            return None
        year = self.publisher_div.text.split()[-2]
        return year

    def find_isbn(self):
        if not self.book_page_exists:
            return None
        isbn_div = book_specs.find('div', 'isbn')

        if isbn_div is not None:
            isbn = isbn_div.text
        else:
            inbn = '-'
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

    # 7. Find annotation text
    def find_annotation_text(self):
        if not self.book_page_exists:
            return None
        about_div = self.source.find('div', id='product-about')
        annotation = about_div.p.text

    def return_result(self):
        debug_result_string = """\n
        ----------------------------
        book No. {}
        ---------
        1. Title: {};
        2. Authors: {};
        3. Publisher: {};
        4. Year: {};
        5. ISBN: {};
        6. Cover image URL: {};
        7. Annotation: {} 
        """
        debug_result_string = debug_result_string.format(book_number, book_title, author, publisher, year, isbn, image_url, annotation)

        return debug_result_string


if __name__ == '__main__':
    for i in range(10):
        parse_single_book_page(i)