from dataclasses import asdict
import csv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(filename)s | %(levelname)s: %(message)s')


def save_list_of_dataclass_objs_to_csv(list_of_dataclass_objs):
    try:
        keys = asdict(list_of_dataclass_objs[0]).keys()
        with open('books_from_resource.csv', 'w') as target_file:
            dict_writer = csv.DictWriter(target_file, fieldnames=keys)
            list_of_dicts = [asdict(dc_obj) for dc_obj in list_of_dataclass_objs]
            logger.debug(list_of_dicts)
            dict_writer.writeheader()
            dict_writer.writerows(list_of_dicts)
            target_file.close()
        logger.info('Data was successfully saved to books_from_resource.csv')
    except IndexError:
        logger.error('It seems the input list is empty (IndexError), nothing to save into csv.')
    except Exception as current_exception:
        logger.error('Sorry, saving to csv failed,'
                     f' because of following exception:\n{current_exception}')
