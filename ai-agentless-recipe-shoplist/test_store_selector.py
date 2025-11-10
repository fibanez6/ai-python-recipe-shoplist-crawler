import os
import sys

from dotenv import load_dotenv
import rich

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config.logging_config import setup_logging
from app.config.store_config import STORE_CONFIGS

load_dotenv()

logger = setup_logging()


aldi = STORE_CONFIGS.get("aldi")

rich.print(aldi.get_search_url("Cherry Tomatoes in Tomato Juice 400g"))


# https://www.aldi.com.au/results?q=Cherry+Tomatoes+in+Tomato+Juice+400g
# https://www.aldi.com.au/results?q=Cherry%20Tomatoes%20in%20Tomato%20Juice%20400g


# https://dm.apac.cms.aldi.cx/is/image/aldiprodapac/product/jpg/scaleWidth/864/0369db98-cf35-44d5-918c-3218f5934edb/Cherry+Tomatoes+in+Tomato+Juice+400g