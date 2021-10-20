import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    site: str
    parse_number: int
    max_ids: int
    first_id: int
    csv: str


def load_config():
    return AppConfig(
        site=os.environ['SITE_ITEMS_PATTERN'],
        parse_number=int(os.environ['NUMBER_ITEMS_TO_PARSE']),
        max_ids=int(os.environ['MAX_IDS_TO_PROCESS']),
        first_id=int(os.environ['FIRST_ITEM_ID']),
        csv=os.environ['CSV'],
    )
