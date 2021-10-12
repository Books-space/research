from bs4 import BeautifulSoup
import requests
import json

source = requests.get('http://webcache.googleusercontent.com/search?q=cache:https://www.labirint.ru/books/812392/').text

source = BeautifulSoup(source, 'lxml')

book_specs = source.find('div', 'product-description')

authors_div = book_specs.find('div', 'authors')

if authors_div:
    print(authors_div.a.text)

publisher_div = book_specs.find('div', 'publisher')
print(publisher_div.prettify())

year_str = publisher_div.text.split()[-2]
print(year_str)

isbn_div = book_specs.find('div', 'isbn')
print(isbn_div)
if isbn_div is not None:
    isbn = isbn_div.text
    print(isbn)
else:
    inbn = '-'


image_div = source.find('div', id='product-image')
print('IMAGE DIV')
print(image_div.prettify())
src_key = ''
image_url = 'no_path'
if image_div.img.has_attr('src'):
    src_key = 'src'
elif image_div.img.has_attr('data-src'):
    src_key = 'data_src'
print(src_key)
if src_key:
    image_url = image_div.img[src_key]
print(image_url)