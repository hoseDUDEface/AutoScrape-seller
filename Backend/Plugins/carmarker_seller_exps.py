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


class CardMarketSellerExpansionsScraper:
    def get_name(self) -> str:
        return "CardMarketSellerExpansionsScraper"

    def get_description(self) -> str:
        return "Extracts card listing data from a CardMarket seller's inventory."

    def get_version(self) -> str:
        return "1.0.0"

    def parse(self, html: str) -> List[List[ScrapedField]]:
        soup = BeautifulSoup(html, 'html.parser')
        expansion_select = soup.find('select', {'name': 'idExpansion'})

        expansions = []

        for option in expansion_select.find_all('option'):
            if option.text == "All":
                continue

            expansion_id = int(option['value'])
            expansion_name = option.text.rsplit('(', 1)[0].strip()
            card_count = int(option.text.rsplit('(', 1)[1].replace(')', '').strip())

            if expansion_id != '0' and card_count > 0:
                expansions.append([
                    ScrapedField("expansion_id", expansion_id, DataType.INTEGER),
                    ScrapedField("expansion_name", expansion_name, DataType.STRING),
                    ScrapedField("card_count", card_count, DataType.INTEGER)
                ])

        return expansions

    def get_available_fields(self) -> List[ScrapedField]:
        return [
            ScrapedField("expansion_id", 0, DataType.INTEGER, found=False),
            ScrapedField("expansion_name", "", DataType.STRING, found=False),
            ScrapedField("card_count", 0, DataType.INTEGER, found=False)
        ]
