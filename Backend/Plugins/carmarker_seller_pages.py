import re

from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Any, Optional
from enum import Enum, auto


# Define data types enum
class DataType(Enum):
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    URL = auto()


@dataclass
class ScrapedField:
    name: str
    value: Any
    field_type: DataType
    found: bool = True
    description: Optional[str] = None


class CardMarketSellerExpansionsPagesScraper:
    def get_name(self) -> str:
        return "CardMarketSellerExpansionsPagesScraper"

    def get_description(self) -> str:
        return "Extracts card listing data from a CardMarket seller's inventory."

    def get_version(self) -> str:
        return "1.0.0"

    def parse(self, html: str) -> List[List[ScrapedField]]:
        soup = BeautifulSoup(html, 'html.parser')
        pagination_text = soup.find('span', class_='mx-1')

        page_count = 1

        if pagination_text:
            match = re.search(r'Page \d+ of (\d+)', pagination_text.text)
            if match:
                page_count = int(match.group(1))

        page_count = [[ScrapedField("page_count", page_count, DataType.INTEGER)]]

        return page_count

    def get_available_fields(self) -> List[ScrapedField]:
        return [
            ScrapedField("page_count", 0, DataType.INTEGER, found=False),
        ]
