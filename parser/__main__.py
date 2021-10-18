import logging
from parser.book_site_parser import SiteParser
from parser.save_dataclass_list_into_csv import save_list_of_dataclass_objs_to_csv
from parser.config import (resource_url, robots_txt, num_items_to_parse, max_id_num_to_process,
                           first_item_id)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(filename)s | %(levelname)s: %(message)s')


if __name__ == '__main__':
    site_parser = SiteParser(url=resource_url,
                             robots_txt=robots_txt,
                             books_number=num_items_to_parse,
                             max_ids_to_process=max_id_num_to_process,
                             first_book_id=first_item_id)
    logger.info('Start.')
    resulting_books = site_parser.parse()
    logger.debug('Resulting book list now is about to be saved to csv!')
    save_list_of_dataclass_objs_to_csv(resulting_books)
    logger.info('The Chore complete.')
