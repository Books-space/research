import logging
from urllib.parse import urlparse

from research.parsers.sites import SiteParser
from research.storage import BookStorage

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s | %(levelname)s: %(message)s',  # noqa: WPS323
)


def run(site, count, max_urls, start, csv_file):
    parse_result = urlparse(site)

    scheme = parse_result.scheme
    netloc = parse_result.netloc

    robots = f'{scheme}://{netloc}/robots.txt'

    site_parser = SiteParser(
        url=site,
        robots=robots,
        count=count,
        max_checks=max_urls,
        start=start,
    )

    books = site_parser.parse()
    BookStorage().to_csv(books, csv_file)
