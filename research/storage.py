import logging

from dataclass_csv import DataclassWriter

from research.domain import Book

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s | %(levelname)s: %(message)s',  # noqa: WPS323
)


class BookStorage:

    def to_csv(self, books: list[Book], filename: str) -> None:
        logger.debug('Resulting book list now is about to be saved to csv!')

        try:
            with open(filename, 'w') as csvfile:
                writer = DataclassWriter(csvfile, books, Book)
                writer.write()

            logger.info('Data was successfully saved to %s', filename)
        except IndexError:
            logger.exception('It seems the input list is empty, nothing to save into csv.')
        except Exception:
            logger.exception('Sorry, saving to csv failed, because of following exception')

        logger.info('Books saved.')
