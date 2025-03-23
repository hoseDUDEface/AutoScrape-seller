from dataclasses import dataclass
from typing import Any, Optional, List, Type, Union
from enum import Enum, auto
from bs4 import BeautifulSoup
from templated_plugin import ScrapedField, DataType

class DataAnalysisPlugin:
    """Base plugin that performs general HTML analysis."""
    
    def get_name(self) -> str:
        """Return the name of the plugin."""
        return "Data Analysis Analysis"
    
    def get_description(self) -> str:
        """Return a description of what the plugin extracts."""
        return "Extracts universal page metrics and structures to aid further scraping"
    
    def get_version(self) -> str:
        """Return the version of the plugin."""
        return "1.0.0"
    
    def parse(self, html: str) -> List[ScrapedField]:
        """
        Parse HTML content and extract basic page metrics.
        
        Args:
            html: Raw HTML string
            
        Returns:
            List of ScrapedField objects with universal page data
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Page size metrics
        results.append(ScrapedField(
            name="page_size_chars",
            value=len(html),
            field_type=DataType.INTEGER,
            description="Total character count of the HTML"
        ))
        
        # Page title
        title = soup.title.text.strip() if soup.title else None
        results.append(ScrapedField(
            name="page_title",
            value=title,
            field_type=DataType.STRING,
            found=title is not None,
            description="Title of the web page"
        ))
        
        # Link count
        results.append(ScrapedField(
            name="link_count",
            value=len(soup.find_all('a')),
            field_type=DataType.INTEGER,
            description="Number of links on the page"
        ))
        
        # Image count
        results.append(ScrapedField(
            name="image_count",
            value=len(soup.find_all('img')),
            field_type=DataType.INTEGER,
            description="Number of images on the page"
        ))
        
        # Main content text estimation
        main_content = self._find_main_content(soup)
        results.append(ScrapedField(
            name="main_content_text",
            value=main_content.get_text(strip=True)[:1000] if main_content else None,
            field_type=DataType.STRING,
            found=main_content is not None,
            description="First 1000 chars of the main content area"
        ))
        
        # HTML structural info - helps identify content patterns
        results.append(ScrapedField(
            name="heading_structure",
            value=self._get_heading_structure(soup),
            field_type=DataType.OBJECT,
            description="Count of heading tags by level (h1-h6)"
        ))
        
        return results
    
    def _find_main_content(self, soup):
        """Identify the likely main content container based on text density."""
        candidates = soup.find_all(['div', 'article', 'section', 'main'])
        if not candidates:
            return None
            
        # Find the element with the most text
        return max(
            candidates,
            key=lambda x: len(x.get_text(strip=True)),
            default=None
        )
    
    def _get_heading_structure(self, soup):
        """Extract heading tag counts to understand page structure."""
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = len(soup.find_all(f'h{i}'))
        return headings