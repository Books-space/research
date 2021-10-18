import logging
from parser.book_site_parser import SiteParser
from parser.save_dataclass_list_into_csv import save_list_of_dataclass_objs_to_csv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(filename)s | %(levelname)s: %(message)s')


def run_parser_and_save_results(url='https://www.labirint.ru/books/{}/',
                                robots_txt='https://www.labirint.ru/robots.txt',
                                num_books_to_parse=2,
                                max_ids_to_process=1,
                                first_book_id=30010):
    site_parser = SiteParser(url=url,
                             robots_txt=robots_txt,
                             books_number=num_books_to_parse,
                             max_ids_to_process=max_ids_to_process,
                             first_book_id=first_book_id)
    logger.info('Start.')
    resulting_books = site_parser.parse()
    logger.debug('Resulting book list now is about to be saved to csv!')
    save_list_of_dataclass_objs_to_csv(resulting_books)
    logger.info('The Chore complete.')


if __name__ == '__main__':
    run_parser_and_save_results()
