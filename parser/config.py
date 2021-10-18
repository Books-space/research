import os

resource_url = os.environ['SITE_ITEMS_PATTERN']
robots_txt = os.environ['ROBOTS_TXT']
num_items_to_parse = int(os.environ['NUMBER_ITEMS_TO_PARSE'])
max_id_num_to_process = int(os.environ['MAX_IDS_TO_PROCESS'])
first_item_id = int(os.environ['FIRST_ITEM_ID'])
