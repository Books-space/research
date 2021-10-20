import logging
from urllib.parse import urlparse

from research.config import load_config
from research.parsers.sites import SiteParser
from research.storage import BookStorage

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

    robots = f'{scheme}://{netloc}/robots.txt'

    site_parser = SiteParser(
        url=config.site,
        robots=robots,
        count=config.parse_number,
        max_checks=config.max_ids,
        start=config.first_id,
    )

    books = site_parser.parse()
    BookStorage().to_csv(books, config.csv)
