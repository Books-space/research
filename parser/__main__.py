import logging
from parser.book_site_parser import SiteParser
from parser.config import load_config
from parser.save_dataclass_list_into_csv import save_list_of_dataclass_objs_to_csv
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s | %(levelname)s: %(message)s',  # noqa: WPS323
)


if __name__ == '__main__':
    config = load_config()
    parse_result = urlparse(config.site.format(config.first_id))
    scheme = parse_result.scheme
    netloc = parse_result.netloc

    robots_txt = f'{scheme}://{netloc}/robots.txt'

    site_parser = SiteParser(
                  url=config.site,
                  robots_txt=robots_txt,
                  books_number=config.parse_number,
                  max_ids_to_process=config.max_ids,
                  first_book_id=config.first_id,
                  )
    logger.info('Start.')
    resulting_books = site_parser.parse()
    logger.debug('Resulting book list now is about to be saved to csv!')
    save_list_of_dataclass_objs_to_csv(resulting_books)
    logger.info('The Chore complete.')
