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


class CardMarketSellerScraper:
    def get_name(self) -> str:
        return "CardMarketSellerScraper"

    def get_description(self) -> str:
        return "Extracts card listing data from a CardMarket seller's inventory."

    def get_version(self) -> str:
        return "1.0.0"

    def parse(self, html: str) -> List[List[ScrapedField]]:
        soup = BeautifulSoup(html, 'html.parser')
        card_rows = soup.select(".article-row")

        parsed_cards = []
        for row in card_rows:
            # Extract card name
            card_name_tag = row.select_one(".col-sellerProductInfo a")
            card_name = card_name_tag.text.strip() if card_name_tag else None

            # Extract expansion name
            expansion_tag = row.select_one(".expansion-symbol")
            expansion = expansion_tag["aria-label"] if expansion_tag else None

            # Extract rarity
            rarity_tag = row.select_one("svg[aria-label]")
            rarity = rarity_tag["aria-label"] if rarity_tag else None

            # Extract condition
            condition_tag = row.select_one(".article-condition")
            condition = condition_tag.text.strip() if condition_tag else None

            # Extract language
            language_tag = row.select_one(".icon[aria-label]")
            language = language_tag["aria-label"] if language_tag else None

            # Extract foil status
            foil_tag = row.select_one(".st_SpecialIcon[aria-label='Foil']")
            is_foil = foil_tag is not None

            # Extract quantity
            quantity_tag = row.select_one(".item-count")
            quantity = int(quantity_tag.text.strip()) if quantity_tag else None

            # Extract price
            price_tag = row.select_one(".color-primary")
            price = float(price_tag.text.replace("€", "").replace(",", ".").strip()) if price_tag else None

            parsed_cards.append([
                ScrapedField("card_name", card_name, DataType.STRING),
                ScrapedField("expansion", expansion, DataType.STRING),
                ScrapedField("rarity", rarity, DataType.STRING),
                ScrapedField("condition", condition, DataType.STRING),
                ScrapedField("language", language, DataType.STRING),
                ScrapedField("is_foil", is_foil, DataType.BOOLEAN),
                ScrapedField("quantity", quantity, DataType.INTEGER),
                ScrapedField("price", price, DataType.FLOAT)
            ])

        return parsed_cards

    def get_available_fields(self) -> List[ScrapedField]:
        return [
            ScrapedField("card_name", "", DataType.STRING, found=False),
            ScrapedField("expansion", "", DataType.STRING, found=False),
            ScrapedField("rarity", "", DataType.STRING, found=False),
            ScrapedField("condition", "", DataType.STRING, found=False),
            ScrapedField("language", "", DataType.STRING, found=False),
            ScrapedField("is_foil", False, DataType.BOOLEAN, found=False),
            ScrapedField("quantity", 0, DataType.INTEGER, found=False),
            ScrapedField("price", 0.0, DataType.FLOAT, found=False)
        ]
