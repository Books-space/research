import logging
from random import randint, uniform
from time import sleep

import httpx

from research.domain import Book
from research.parsers.pages import PageParser

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s | %(levelname)s: %(message)s',  # noqa: WPS323
)


class SiteParser:

    def __init__(self, url, robots, start=30010, count=10, max_checks=500):
        self.url = url
        self.robots = robots
        self.start = start
        self.count = count
        self.max_checks = max_checks

    def parse(self) -> list[Book]:
        logger.info('Start.')

        parsed_books_num = 0
        processed_urls = 0
        current_id = self.start
        books = []
        try:
            while parsed_books_num < self.count and processed_urls < self.max_checks:
                if processed_urls > 0:
                    self.pause()
                    increment = randint(1, 10)
                    current_id += increment
                    logger.debug('Random increment [1, 10]: %s;' % increment)
                logger.debug('So current id: %s;' % current_id)
                processed_urls += 1
                logger.info('Processing url No.: %s;' % processed_urls)

                try:
                    book_parser = PageParser(
                        book_id=current_id,
                        base_url=self.url,
                        robots_txt=self.robots,
                    )
                    book_parser.load()
                    book = book_parser.return_result()
                    if book is not None:
                        books.append(book)
                        parsed_books_num += 1
                        logger.info('Success: done: %s of %s;' % (parsed_books_num, self.count))
                    else:
                        logger.debug('Not book url, skip;')
                        logger.info('Fail: done: %s of %s;' % (parsed_books_num, self.count))
                    logger.info('Processed ids: %s of %s;' % (processed_urls, self.max_checks))
                except httpx.HTTPError:
                    logger.debug('Book id: %s' % current_id, exc_info=True)
                except Exception as exc:
                    logger.exception('Book id: %s - %s;' % (current_id, exc))
        except KeyboardInterrupt:
            logger.info('\n\n\n...OK! Parsing was interrupted from keyboard.')

        return books

    def pause(self, min_period=0.9, max_period=3.1):
        pause_period = uniform(min_period, max_period)
        logger.debug('wait for: %s sec.' % pause_period)
        sleep(pause_period)
