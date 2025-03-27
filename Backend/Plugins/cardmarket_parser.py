from dataclasses import dataclass
from typing import Any, Optional, List, Type, Union
from bs4 import BeautifulSoup
from templated_plugin import ScrapedField, DataType

class CardmarketPricePlugin:
    """Plugin that extracts price information from Cardmarket pages."""
    
    def get_name(self) -> str:
        """Return the name of the plugin."""
        return "Cardmarket Price Plugin"
    
    def get_description(self) -> str:
        """Return a description of what the plugin extracts."""
        return "Extracts price information from Cardmarket product pages across different games and languages"
    
    def get_version(self) -> str:
        """Return the version of the plugin."""
        return "1.0.0"
    
    def get_available_fields(self) -> List[ScrapedField]:
        """
        Returns a list of all possible fields this plugin can extract, with realistic default values.
        
        Returns:
            List of ScrapedField objects with default values
        """
        return [
            ScrapedField(
                name="available_items",
                value=500,
                field_type=DataType.INTEGER,
                description="Number of available items for sale",
                accumulate=True
            ),
            ScrapedField(
                name="lowest_price",
                value="1,00 €",
                field_type=DataType.STRING,
                description="Lowest price available for the card",
                accumulate=True
            ),
            ScrapedField(
                name="price_trend",
                value="5,00 €",
                field_type=DataType.STRING,
                description="Price trend of the card",
                accumulate=True
            ),
            ScrapedField(
                name="avg_30_days",
                value="4,75 €",
                field_type=DataType.STRING,
                description="Average price over the last 30 days",
                accumulate=True
            ),
            ScrapedField(
                name="avg_7_days",
                value="4,50 €",
                field_type=DataType.STRING,
                description="Average price over the last 7 days",
                accumulate=True
            ),
            ScrapedField(
                name="avg_1_day",
                value="4,25 €",
                field_type=DataType.STRING,
                description="Average price over the last day",
                accumulate=True
            ),
            ScrapedField(
                name="card_rarity",
                value="Uncommon",
                field_type=DataType.STRING,
                description="Rarity of the card",
                accumulate=True
            ),
            ScrapedField(
                name="card_number",
                value="123",
                field_type=DataType.STRING,
                description="Card number in the set",
                accumulate=True
            ),
            ScrapedField(
                name="card_expansion",
                value="Example Set",
                field_type=DataType.STRING,
                description="Expansion/set the card belongs to",
                accumulate=True
            )
        ]

    def parse(self, html: str) -> List[ScrapedField]:
        """
        Parse HTML content and extract Cardmarket price information.
        
        Args:
            html: Raw HTML string
            
        Returns:
            List of ScrapedField objects with price data
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find the info container using a class-based selector
        container = soup.select_one('.info-list-container')
        
        if not container:
            # If we can't find the container, return empty results
            return results
            
        # Find the definition list containing the key-value pairs
        dl = container.select_one('dl')
        if not dl:
            return results
            
        # Extract all definition terms and values
        dt_elements = dl.select('dt')
        dd_elements = dl.select('dd')
        
        # Create a dictionary to map field keys to values
        price_data = {}
        for i in range(min(len(dt_elements), len(dd_elements))):
            key = dt_elements[i].get_text().strip()
            # For the value, extract the text or try to find a specific span
            value_elem = dd_elements[i].select_one('span')
            value = value_elem.get_text().strip() if value_elem else dd_elements[i].get_text().strip()
            price_data[key] = value
        
        # Extract available items
        available_items_value = None
        for key in price_data:
            if any(term in key.lower() for term in ['available', 'artikel', 'articles']):
                available_items_value = price_data[key]
                # Try to convert to integer
                try:
                    available_items_value = int(''.join(c for c in available_items_value if c.isdigit()))
                except (ValueError, TypeError):
                    pass
                break
        
        if available_items_value is not None:
            results.append(ScrapedField(
                name="available_items",
                value=available_items_value,
                field_type=DataType.INTEGER if isinstance(available_items_value, int) else DataType.STRING,
                description="Number of available items for sale",
                accumulate=True
            ))
        
        # Extract lowest price
        lowest_price = None
        for key in price_data:
            if any(term == key.lower() for term in ['from', 'de', 'ab']):
                lowest_price = price_data[key]
                break
        
        if lowest_price:
            results.append(ScrapedField(
                name="lowest_price",
                value=lowest_price,
                field_type=DataType.STRING,
                description="Lowest price available for the card",
                accumulate=True
            ))
        
        # Extract price trend
        price_trend = None
        for key in price_data:
            if any(term in key.lower() for term in ['trend', 'tendance']):
                price_trend = price_data[key]
                break
        
        if price_trend:
            results.append(ScrapedField(
                name="price_trend",
                value=price_trend,
                field_type=DataType.STRING,
                description="Price trend of the card",
                accumulate=True
            ))
        
        # Extract 30-day average
        avg_30_days = None
        for key in price_data:
            if '30' in key and any(term in key.lower() for term in ['day', 'jour', 'tage']):
                avg_30_days = price_data[key]
                break
        
        if avg_30_days:
            results.append(ScrapedField(
                name="avg_30_days",
                value=avg_30_days,
                field_type=DataType.STRING,
                description="Average price over the last 30 days",
                accumulate=True
            ))
        
        # Extract 7-day average
        avg_7_days = None
        for key in price_data:
            if '7' in key and any(term in key.lower() for term in ['day', 'jour', 'tage']):
                avg_7_days = price_data[key]
                break
        
        if avg_7_days:
            results.append(ScrapedField(
                name="avg_7_days",
                value=avg_7_days,
                field_type=DataType.STRING,
                description="Average price over the last 7 days",
                accumulate=True
            ))
        
        # Extract 1-day average
        avg_1_day = None
        for key in price_data:
            if '1' in key and any(term in key.lower() for term in ['day', 'jour', 'tage']):
                avg_1_day = price_data[key]
                break
        
        if avg_1_day:
            results.append(ScrapedField(
                name="avg_1_day",
                value=avg_1_day,
                field_type=DataType.STRING,
                description="Average price over the last day",
                accumulate=True
            ))
        
        # Extract card rarity
        card_rarity = None
        for key in price_data:
            if any(term in key.lower() for term in ['rarity', 'rareté', 'rarität']):
                card_rarity = price_data[key]
                break
        
        if card_rarity:
            results.append(ScrapedField(
                name="card_rarity",
                value=card_rarity,
                field_type=DataType.STRING,
                description="Rarity of the card",
                accumulate=True
            ))
        
        # Extract card number
        card_number = None
        for key in price_data:
            if any(term in key.lower() for term in ['number', 'nombre', 'nummer']):
                card_number = price_data[key]
                break
        
        if card_number:
            results.append(ScrapedField(
                name="card_number",
                value=card_number,
                field_type=DataType.STRING,
                description="Card number in the set",
                accumulate=True
            ))
        
        # Extract card expansion
        card_expansion = None
        for key in price_data:
            if any(term in key.lower() for term in ['printed in', 'edité dans', 'erschienen in']):
                card_expansion = price_data[key]
                break
        
        if card_expansion:
            results.append(ScrapedField(
                name="card_expansion",
                value=card_expansion,
                field_type=DataType.STRING,
                description="Expansion/set the card belongs to",
                accumulate=True
            ))
        
        return results