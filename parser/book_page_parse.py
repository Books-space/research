import logging
from urllib import robotparser
from random import uniform, randint
from dataclasses import dataclass, asdict
import csv
from bs4 import BeautifulSoup
import httpx


logger = logging.getLogger(__name__)


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


class SiteParser:

    def __init__(self,
                 url,
                 robots_txt,
                 first_book_id=30010,
                 books_number=10, max_ids_to_process=500):

        self.url = url
        self.robots_txt = robots_txt
        self.first_book_id = first_book_id
        self.books_number = books_number
        self.max_ids_to_process = max_ids_to_process

        logger.debug('''Site Parser now initialized with following settings:
        Site URL: {};
        robots.txt URL: {};
        First book id: {};
        Number of books to parse: {};
        Maximum ids to process: {};
        '''.format(url, robots_txt, first_book_id, books_number, max_ids_to_process))

    def parse(self):
        parsed_books_num = 0
        processed_urls = 0
        current_id = self.first_book_id
        books = []
        try:
            while parsed_books_num < self.books_number and \
                  processed_urls < self.max_ids_to_process:
                if processed_urls > 0:
                    self.pause()
                processed_urls += 1
                logger.info(f'Processing url No.: {processed_urls}')
                increment = randint(1, 10)
                current_id += increment
                logger.debug(f'Random increment [1, 10]: {increment};')
                logger.debug(f'So current id: {current_id};')
                try:
                    book_parser = SingleBookPageParser(book_id=current_id,
                                                       base_url=self.url,
                                                       robots_txt=self.robots_txt)
                    book_parser.load()
                    book = book_parser.return_result()
                    if book is not None:
                        logger.debug(book.__repr__())
                        books.append(book)
                        parsed_books_num += 1
                        logger.info(f'Success: done: {parsed_books_num} of {self.books_number};')
                    else:
                        logger.debug('Not book url, skip;')
                        logger.info(f'Fail: done: {parsed_books_num} of {self.books_number};')
                    logger.info(f'Processed ids: {processed_urls} of {self.max_ids_to_process};')
                except httpx.HTTPError:
                    logger.debug(f'Book id: {current_id}', exc_info=True)
                except Exception:
                    logger.exception(f'Book id: {current_id}')
        except KeyboardInterrupt:
            logger.info('\n\n\n...OK! Parsing was interrupted from keyboard.')

        return books

    def pause(self, min_period=0.9, max_period=3.1):
        def wait_and_draw_progressbar(time_quant=1.0):
            width = 10
            logger.debug('{}{}Waiting complete;{}'.format('=' * width, '|', '\n' * 10))

        pause_period = uniform(min_period, max_period)
        quant_period = pause_period / 10
        logger.debug('{}{}'.format('-' * 20, '\n' * 10))
        logger.debug(f'wait for:{pause_period} sec.')
        wait_and_draw_progressbar(time_quant=quant_period)


def save_list_of_dataclass_objs_to_csv(list_of_dataclass_objs):
    try:
        keys = asdict(list_of_dataclass_objs[0]).keys()
        with open('books_from_resource.csv', 'w') as target_file:
            dict_writer = csv.DictWriter(target_file, keys)
            list_of_dicts = [asdict(dc_obj) for dc_obj in list_of_dataclass_objs]
            logger.debug(list_of_dicts)
            dict_writer.writerows(list_of_dicts)
            target_file.close()
        logger.info('Data was successfully saved to books_from_resource.csv')
    except IndexError:
        logger.error('It seems the input list is empty (IndexError), nothing to save into csv.')
    except Exception as current_exception:
        logger.error('Sorry, saving to csv failed,'
                     f' because of following exception:\n{current_exception}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    site_parser = SiteParser(url='https://www.labirint.ru/books/{}/',
                             robots_txt='https://www.labirint.ru/robots.txt',
                             books_number=2,
                             max_ids_to_process=1)
    logger.info('start.')
    resulting_books = site_parser.parse()

    logger.debug('Resulting book list now is about to be saved to csv!')
    save_list_of_dataclass_objs_to_csv(resulting_books)
    logger.info('The Chore complete.')
