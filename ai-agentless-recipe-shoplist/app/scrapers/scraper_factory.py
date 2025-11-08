from typing import Protocol

from app.config.store_config import StoreConfig
from app.scrapers.coles_rapidapi import ColesRapidAPI
from app.scrapers.html_scraper import HTMLScraper


class ScraperProtocol(Protocol):
    async def scrape(self, url: str, store_config: StoreConfig) -> dict:
        ...


class ScraperFactory:
    """Factory class to create scraper instances based on store configuration."""

    @staticmethod
    def create_scraper(store_config: StoreConfig) -> ScraperProtocol:
        if store_config.search_type == "html":
            return HTMLScraper()
        elif store_config.search_type == "coles_rapidapi":
            return ColesRapidAPI()
        else:
            raise ValueError(f"Unknown scraper type: {store_config.search_type}")