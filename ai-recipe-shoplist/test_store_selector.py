import os
import sys

from dotenv import load_dotenv
import rich

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.html_helpers import clean_html_for_ai
from app.services.grocery_service import grocery_service
from app.config.logging_config import setup_logging
from bs4 import BeautifulSoup, Comment

load_dotenv()

logger = setup_logging()


aldi = {
    "name": "aldi",
    "url": "https://www.aldi.com.au/results?q=tomato&limit=12",
    "fetched_search": "tmp/web_cache/content/5ad1fe181ebc52b95a46ca4c68ffdb4d_original.html",
    "html_selectors": {
        "product_tile": ".product-tile",
        "product_name": '.product-tile__name',
        "product_price": '.product-tile__price',
        "product_price_unit": '.product-tile__unit-of-measurement',
        "product_image": '.product-tile__picture img',
        "product_brand": '.product-tile__brandname',
        "product_url": '.product-tile__link'
    }
}

coles = {
    "name": "coles",
    "url": "https://www.coles.com.au/search/products?q=tomatoes&limit=12",
    "fetched_search": "tmp/web_cache/content/6db825b60fa4b95745e8e057696b00c9_original.html",
    "html_selectors": {
        "product_tile": 'section[data-testid="product-tile"]',
        # "product_name": '.product-tile__name',
        # "product_price": '.product-tile__price',
        # "product_price_unit": '.product-tile__unit-of-measurement',
        # "product_image": '.product-tile__picture img',
        # "product_brand": '.product-tile__brandname',
        # "product_url": '.product-tile__link'
    }
}

store = coles

stores = grocery_service.get_stores([store["name"]])
rich.print(stores)

with open(store["fetched_search"], 'r', encoding='utf-8') as f:
    html = f.read()


print("Original HTML length:", len(html))


# cleaned_content = clean_html_for_ai(html, html_selectors)
# rich.print(cleaned_content)

rich.print(f"store name: {store['name']}")

soup = BeautifulSoup(html, 'html.parser')
# tile_elements = soup.select(store["html_selectors"]["product_tile"])
tile_elements = soup.select(".sc-a013a2d1-7")


rich.print(f"Found {len(tile_elements)} product tiles")
rich.print("---------- Sample Product Tile Data: -----------")
rich.print(tile_elements)


tile = tile_elements[1]

rich.print("---------- Sample Product Tile Data: -----------")

filtered_selectors = {k: v for k, v in store["html_selectors"].items() if k != "product_tile"}
for name, selector in filtered_selectors.items():
    element = tile.select_one(selector)
    # print(f"---------- {name}: -----------")
    # if element:
    #     rich.print(element.prettify())
    # else:
    #     print(f"{name}: Not found")

    if element:
        if element.name == "img":
            rich.print(f"{name}: {element.get('src', '')}")
        elif element.name == "a":
            rich.print(f"{name}: {element.get('href', '')}")
        else:
            rich.print(f"{name}: {element.get_text(strip=True)}")

# print("---------- Full Product Tile: -----------")
# rich.print(tile.prettify())



