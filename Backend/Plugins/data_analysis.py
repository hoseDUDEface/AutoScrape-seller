from dataclasses import dataclass
from typing import Any, Optional, List, Type, Union
from enum import Enum, auto
from bs4 import BeautifulSoup
from templated_plugin import ScrapedField, DataType

class DataAnalysisPlugin:
    """Base plugin that performs general HTML analysis."""
    
    def get_name(self) -> str:
        """Return the name of the plugin."""
        return "Data Analysis Plugin"
    
    def get_description(self) -> str:
        """Return a description of what the plugin extracts."""
        return "Extracts universal page metrics and structures to aid further scraping"
    
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
                name="page_size_chars",
                value=45000,  # Average web page size in characters
                field_type=DataType.INTEGER,
                description="Total character count of the HTML",
                accumulate=True  # Accumulate character counts
            ),
            ScrapedField(
                name="page_title",
                value="Example Page Title | Website Name",  # Example title format
                field_type=DataType.STRING,
                found=True,
                description="Title of the web page",
                accumulate=False  # Don't accumulate strings
            ),
            ScrapedField(
                name="link_count",
                value=75,  # Typical number of links on a content page
                field_type=DataType.INTEGER,
                description="Number of links on the page",
                accumulate=True  # Accumulate link counts
            ),
            ScrapedField(
                name="image_count",
                value=12,  # Typical number of images on a content page
                field_type=DataType.INTEGER,
                description="Number of images on the page",
                accumulate=True  # Accumulate image counts
            ),
            ScrapedField(
                name="canonical_url",
                value="https://example.com/page-path/",
                field_type=DataType.URL,
                found=True,
                description="Canonical URL specified in link tags",
                accumulate=False  # Don't accumulate URLs
            ),
            ScrapedField(
                name="content_language",
                value="en-US",
                field_type=DataType.STRING,
                found=True,
                description="Language of the page content",
                accumulate=False  # Don't accumulate language strings
            ),
            ScrapedField(
                name="internal_link_count",
                value=45,
                field_type=DataType.INTEGER,
                description="Number of links to the same domain",
                accumulate=True  # Accumulate internal link counts
            ),
            ScrapedField(
                name="external_link_count",
                value=30,
                field_type=DataType.INTEGER,
                description="Number of links to external domains",
                accumulate=True  # Accumulate external link counts
            )
        ]
    
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
            description="Total character count of the HTML",
            accumulate=True  # Accumulate character counts
        ))
        
        # Page title
        title = soup.title.text.strip() if soup.title else None
        results.append(ScrapedField(
            name="page_title",
            value=title,
            field_type=DataType.STRING,
            found=title is not None,
            description="Title of the web page",
            accumulate=False  # Don't accumulate strings
        ))
        
        # Link count
        results.append(ScrapedField(
            name="link_count",
            value=len(soup.find_all('a')),
            field_type=DataType.INTEGER,
            description="Number of links on the page",
            accumulate=True  # Accumulate link counts
        ))
        
        # Image count
        results.append(ScrapedField(
            name="image_count",
            value=len(soup.find_all('img')),
            field_type=DataType.INTEGER,
            description="Number of images on the page",
            accumulate=True  # Accumulate image counts
        ))
        
        # Find canonical URL if available
        canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
        canonical_url = canonical_tag.get('href', '') if canonical_tag else None
        results.append(ScrapedField(
            name="canonical_url",
            value=canonical_url,
            field_type=DataType.URL,
            found=canonical_url is not None,
            description="Canonical URL specified in link tags",
            accumulate=False  # Don't accumulate URLs
        ))
        
        # Count internal vs external links
        domain = self._extract_domain(canonical_url) if canonical_url else ''
        internal_links = 0
        external_links = 0
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.startswith('#') or not href:
                continue  # Skip anchor links and empty hrefs
            elif href.startswith('/') or (domain and domain in href):
                internal_links += 1
            else:
                external_links += 1
        
        results.append(ScrapedField(
            name="internal_link_count",
            value=internal_links,
            field_type=DataType.INTEGER,
            description="Number of links to the same domain",
            accumulate=True  # Accumulate internal link counts
        ))
        
        results.append(ScrapedField(
            name="external_link_count",
            value=external_links,
            field_type=DataType.INTEGER,
            description="Number of links to external domains",
            accumulate=True  # Accumulate external link counts
        ))
        
        # Find language
        html_tag = soup.find('html')
        lang = html_tag.get('lang', '') if html_tag else None
        if not lang:
            meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
            lang = meta_lang.get('content', '') if meta_lang else None
        
        results.append(ScrapedField(
            name="content_language",
            value=lang,
            field_type=DataType.STRING,
            found=lang is not None and lang != '',
            description="Language of the page content",
            accumulate=False  # Don't accumulate language strings
        ))
        
        return results
    
    def _extract_domain(self, url):
        """Extract domain from URL."""
        if not url:
            return ''
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            return parsed_url.netloc
        except:
            # Simple fallback if urllib is not available
            url = url.replace('http://', '').replace('https://', '')
            return url.split('/')[0]