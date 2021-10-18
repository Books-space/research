import logging
from random import uniform, randint
import httpx
from parser.book_page_parse import SingleBookPageParser

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s | %(levelname)s: %(message)s',  # noqa: WPS323
)


class SiteParser:

    def __init__(self,
                 url,
                 robots_txt,
                 first_book_id=30010,
                 books_number=10,
                 max_ids_to_process=500):

        self.url = url
        self.robots_txt = robots_txt
        self.first_book_id = first_book_id
        self.books_number = books_number
        self.max_ids_to_process = max_ids_to_process

        debug_str = '''Site Parser now initialized with following settings:
        Site URL: {};
        robots.txt URL: {};
        First book id: {};
        Number of books to parse: {};
        Maximum ids to process: {};
        '''

        logger.debug(debug_str.format(
                     url, 
                     robots_txt,
                     first_book_id,
                     books_number,
                     max_ids_to_process,
        )
        )

    def parse(self):
        parsed_books_num = 0
        processed_urls = 0
        current_id = self.first_book_id
        books = []
        try:
            while parsed_books_num < self.books_number and processed_urls < self.max_ids_to_process:
                if processed_urls > 0:
                    self.pause()
                    increment = randint(1, 10)
                    current_id += increment
                    logger.debug(f'Random increment [1, 10]: {increment};')
                logger.debug(f'So current id: {current_id};')
                processed_urls += 1
                logger.info(f'Processing url No.: {processed_urls}')
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
