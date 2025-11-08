import logging
from functools import partial
import traceback
import requests

from app.config.pydantic_config import RAPID_API_SETTINGS
from app.config.store_config import StoreConfig

from ..config.logging_config import get_logger, log_function_call

logger = get_logger(__name__)

class ColesRapidAPI:
    def __init__(self):
        self.name = "ColesRapidAPI"
        self.api_key = RAPID_API_SETTINGS.api_key

        self.headers = {
            "x-rapidapi-key": self.api_key
        }

        logger.debug(f"Initialized {self.name}")

    async def query(self, query):
        try:
            # Construct the API URL
            url = "https://coles-product-price-api.p.rapidapi.com/coles/product-search?query=tomato&size=5"

            # Query parameters
            # params = {
            #     "query": query

            # }
            
            # Make the GET request
            response = requests.get(url, headers=self.headers)

            # Check if request was successful
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Response data keys: {list(data.keys())}")
                # logger.debug(f"Response data preview: {data.get('results', [])[:2]}")
                logger.debug(f"Response data preview: {data.get('results', [])}")

            logger.info(f"Successfully fetched data for query: '{query}' and received {len(data.get('results', []))} products.")

            return data.get("results", [])

        except Exception as e:
            logger.error(f"Error occurred while querying: {e}")
            raise

    def search_products(self, query):        
        logger.debug(f"Searching products with query: {query}")
        return self.query(query)
    
    async def scrape(self, url: str, store_config: StoreConfig) -> dict:
        """Scrape a web page and return processed data."""
        logger.info(f"{self.name}: Scraping URL: {url}")

        # Extract query string after '?'
        if '?' in url:
            query_string = url.split('?', 1)[1]
        else:
            query_string = ""


        result = await self.query(query_string)
        return {
            "data": result,
            "data_from": "Coles RapidAPI",
            "data_size": len(str(result)),
            "data_format": "json"
        }
