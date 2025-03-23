from dataclasses import dataclass
from typing import Any, Optional, List, Type, Union
from enum import Enum, auto

# Define data types enum for clarity
class DataType(Enum):
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    DATE = auto()
    DATETIME = auto()
    URL = auto()
    IMAGE = auto()
    ARRAY = auto()
    OBJECT = auto()
    # Add more types as needed

@dataclass
class ScrapedField:
    """Represents a single piece of data extracted from HTML."""
    name: str
    value: Any
    field_type: DataType
    found: bool = True
    description: Optional[str] = None
    
    def __post_init__(self):
        # Optional: Add validation here to ensure value matches field_type
        pass

class ScraperPlugin:
    """Base class for all scraper plugins."""
    
    def get_name(self) -> str:
        """Return the name of the plugin."""
        return self.__class__.__name__
    
    def get_description(self) -> str:
        """Return a description of what the plugin extracts."""
        return "Base scraper plugin"
    
    def get_version(self) -> str:
        """Return the version of the plugin."""
        return "1.0.0"
    
    def parse(self, html: str) -> List[ScrapedField]:
        """
        Parse HTML content and extract structured data.
        
        Args:
            html: Raw HTML string
            
        Returns:
            List of ScrapedField objects
        """
        raise NotImplementedError("Plugins must implement parse()")