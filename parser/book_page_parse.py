from bs4 import BeautifulSoup
import requests
import json


GOOGLE_CACHE_PATH = 'http://webcache.googleusercontent.com/search?q=cache:'
BOOK_BASE_URL = 'https://www.labirint.ru/books/81239{}/'


def parse_single_book_page(book_number):
    request_result = requests.get(''.join((GOOGLE_CACHE_PATH, BOOK_BASE_URL.format(book_number))))
    code = request_result.status_code
    if code < 200 or code > 299:
        print(f'\n-----\nPage doesn\'t exist for book {book_number}. Status code {code}')
        return

    source = BeautifulSoup(request_result.text, 'lxml')

    # 1. Find book title
    title_div = source.find('div', 'prodtitle')
    book_title = title_div.h1.text


    # Find book specs block
    book_specs = source.find('div', 'product-description')


    # 2. Find authors
    authors_div = book_specs.find('div', 'authors')
    if authors_div:
        author = authors_div.a.text
    else:
        author = '-'


    # 3. Find publisher
    publisher_div = book_specs.find('div', 'publisher')
    publisher = publisher_div.a.text


    # 4. Year
    year = publisher_div.text.split()[-2]


    # 5. ISBN
    isbn_div = book_specs.find('div', 'isbn')

    if isbn_div is not None:
        isbn = isbn_div.text
    else:
        inbn = '-'


    # 6. Find cover image url
    image_div = source.find('div', id='product-image')
    src_key = ''
    image_url = 'no_path'
    if image_div.img.has_attr('src'):
        src_key = 'src'
    elif image_div.img.has_attr('data-src'):
        src_key = 'data_src'
    if src_key:
        image_url = image_div.img[src_key]


    # 7. Find annotation text
    about_div = source.find('div', id='product-about')
    annotation = about_div.p.text

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

    print(debug_result_string)


if __name__ == '__main__':
    for i in range(10):
        parse_single_book_page(i)