

![autoscrape](https://github.com/user-attachments/assets/89937604-8c96-40f0-af4f-c34996a31e40)
<p align="center" style="font-size: 28px;">
  Scrape a list of urls with 10 different technologies, automatically, and parse the results with your own custom plugin.
</p>
<p align="center">
  <a href="https://discord.com/invite/a3urQuhcC5">
    <img src="https://dcbadge.limes.pink/api/server/a3urQuhcC5?style=flat-square" alt="Join us on discord!" />
  </a>
</p>



## Disclaimer

<details>
<summary>About this project</summary>

This project was made using the infamous method of **vibe coding**, using Claude 3.7. I understand most of it, but the javascript using [Ulixee Hero](https://github.com/ulixee/hero) is not something i'm comfortable with. I highly encourage anyone who wants to modify it to do so. If anyone wants to fork it and update it regularly, be my guest, and I'll reference you there.
</details>

<details>
<summary>About testing environment</summary>

All testing was performed on Windows 11 with Python 3.12.4 and the latest versions of supported browsers. Performance and compatibility with other operating systems cannot be guaranteed. Users on Linux or MacOS may need to modify certain components to achieve functionality.
</details>

<details>
<summary>About liability</summary>

This software is provided for personal use in a protected environment only. I cannot and will not be held responsible for any misuse, illegal use, or any damages that may occur from using this software. Users are solely responsible for ensuring they comply with all applicable laws, terms of service, and policies when using this tool. By downloading or using this software, you acknowledge that you assume all risks associated with its use.
</details>

## Software View
![image](https://github.com/user-attachments/assets/167de176-eb6a-43ad-815c-53b39289b95b)

## Example 

<div align="center">
  <h2>Comparison: Headless vs Not Headless Mode</h2>
  <table>
    <tr>
      <th>Hero + stealth Not Headless</th>
      <th>Standard Selenium Headless</th>
    </tr>
    <tr>
      <td>
        <video src="https://github.com/user-attachments/assets/628388e5-0e39-4bdd-9fbf-a7ce5a0189fd" controls width="400"></video>
      </td>
      <td>
        <video src="https://github.com/user-attachments/assets/e24171c9-5062-455e-b06e-d188c48d68e7" controls width="400"></video>
      </td>
    </tr>
  </table>
</div>

## Setup
Run the script setup.bat to :
1) Install Python3 if not installed
2) Install all the python dependencies
3) Install npm / javascript if not installed
4) Install npm dependencies

## Usage
To launch AutoScrape, you may either run autoscrape.bat or go in the Backend folder and run `python autoscrape.py`.

### Simple plug and play
1) Enter a url in the url list textbox
2) Chose your technology. Selenium standard is fast but not very discrete. Ulixee hero stealth is very slow bu very hard to detect. Everything has downside and upsides.
3) Chose wether to run it in headless (in background) or not (a browser window will open). Headless is easier to detect by anti-bot technologies.
4) Click Run
5) If the page was accessed and no cloudflare page was detected, the html is saved in `Backend/scraped_html/`

### Advanced Usage
#### Input
A list of urls instead of a single url can be used, either by pasting it, or loading, in .txt format, using the Load URLs button. All urls are *consumed* by the execution, each time one is scraped, it is removed from the list. 

#### Scraping technologies
[Selenium](https://github.com/SeleniumHQ/selenium) is a webdriver made for browser automation.
* Selenium Standard is the default. It is very fast, but not very stealthy. It is easily detectable but works for basic usage or unprotected websites.
* Selenium Stealth is just like selenium standard, but uses the [selenium_stealth](https://github.com/fedorenko22116/selenium-stealth) module, a bit more secure and undetected. Selenium stealth has not been updated for four years though.
* Selenium Undetected uses a different chromedriver, [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver), made for stealth. It has not been updated for a year.
* Selenium Base uses a different selenium, [SeleniumBase](https://github.com/seleniumbase/SeleniumBase), built for scraping. It is much better than selenium. AutoScrape is not using SeleniumBase at its fullest, I might update this in the future.


[Ulixee Hero](https://github.com/ulixee/hero) is a browser built for scraping. It uses selenium for scraping, but is way less detectable.
* Hero Standard is the default. It runs with normal settings.
* Hero Puppeteer runs hero alongside [puppeteer](https://github.com/puppeteer/puppeteer), an API made to control Chrome and Firefox, and is good for scraping.
* Hero Extra runs hero alongside [puppeteer-extra](https://github.com/berstend/puppeteer-extra), which enables plugin usage. This option automatically uses the [puppeteer-extra-plugin-stealth](https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth) plugin for basic undetectability.
* Hero Stealth is an enhanced version that uses multiple undetection plugins including:
  * puppeteer-extra-plugin-stealth
  * puppeteer-extra-plugin-anonymize-ua
  * puppeteer-extra-plugin-block-resources
  * puppeteer-extra-plugin-user-preferences
  * puppeteer-extra-plugin-user-data-dir
  * puppeteer-extra-plugin-font-size
  * puppeteer-extra-plugin-click-and-wait
  * puppeteer-extra-plugin-proxy (if configured)
  * puppeteer-extra-plugin-random-user-agent

  [Playwright](https://github.com/microsoft/playwright) is a framework made by Microsoft for web testing and automation.
  * Playwright standard is the basic experience
  * Playwright puppeteer+stealth is similar to the ulixe hero extra, but using [playwright extra](https://github.com/berstend/puppeteer-extra/tree/master/packages/playwright-extra) instead of puppeteer extra


#### Human Behavior
Human Behavior is just some tweak which adds in some scrolling, clicking etc to appear more humane, with a low to high setting. I have not tested this much, i advice just not using it, and it's useless in headless.

#### Headless
Headless mode runs the browser without showing a window.

- **Headless (True)**: Way faster and lets you use your computer while scraping happens in background. Easier for websites to detect as a bot though.

- **Not Headless (False)**: Browser window opens and takes over your screen, making it unusable while scraping. Slower but way harder to detect. Use this for heavily protected websites.

#### Using Plugins
By default, AutoScrape only saves the raw HTML of scraped pages to the `Backend/scraped_html/` directory. To extract structured data:

1. Select a plugin from the dropdown menu in the interface
2. When you run the scraper, it will process the HTML with your selected plugin
3. Extracted data is saved as CSV files in `Backend/scraped_data/`

This lets you automatically extract specific information like prices, product details, or other structured data from the scraped websites.

## Creating Custom Plugins

AutoScrape supports custom parser plugins that can extract specific data from the scraped HTML. These plugins process websites you scrape and output structured data.

### Plugin Structure

Plugins are Python classes with a specific interface. Each plugin must:

1. Be placed in the `Backend/plugins` directory
2. Import the necessary modules (`ScrapedField` and `DataType` from `templated_plugin`)
3. Implement all required interface methods

### Basic Plugin Template

<details>
<summary>Click to view basic plugin template</summary>

```python
from dataclasses import dataclass
from typing import Any, List, Optional, Type, Union
from bs4 import BeautifulSoup
from templated_plugin import ScrapedField, DataType

class MyCustomPlugin:
    """Plugin that extracts specific data from a website."""
    
    def get_name(self) -> str:
        """Return the name of the plugin."""
        return "My Custom Plugin"
    
    def get_description(self) -> str:
        """Return a description of what the plugin extracts."""
        return "Extracts important data from my favorite website"
    
    def get_version(self) -> str:
        """Return the version of the plugin."""
        return "1.0.0"
    
    def get_available_fields(self) -> List[ScrapedField]:
        """
        Returns all possible fields this plugin can extract, with default values.
        """
        return [
            ScrapedField(
                name="title",
                value="Example Title",
                field_type=DataType.STRING,
                description="The title of the page",
                accumulate=True
            ),
            ScrapedField(
                name="price",
                value="$19.99",
                field_type=DataType.STRING,
                description="The price of the item",
                accumulate=True
            )
        ]

    def parse(self, html: str) -> List[ScrapedField]:
        """
        Parse HTML content and extract data.
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Extract title
        title_element = soup.select_one('h1.product-title')
        if title_element:
            results.append(ScrapedField(
                name="title",
                value=title_element.get_text().strip(),
                field_type=DataType.STRING,
                description="The title of the page",
                accumulate=True
            ))
        
        # Extract price
        price_element = soup.select_one('span.price')
        if price_element:
            results.append(ScrapedField(
                name="price",
                value=price_element.get_text().strip(),
                field_type=DataType.STRING,
                description="The price of the item",
                accumulate=True
            ))
        
        return results
```
</details>

### The ScrapedField Class

The `ScrapedField` class defines the data fields your plugin extracts:

- **name**: Identifier for the field
- **value**: The extracted value
- **field_type**: Data type (STRING, INTEGER, FLOAT, BOOLEAN, etc.)
- **description**: Human-readable description of the field
- **accumulate**: Whether to collect multiple values for this field across scrapes

### Data Types

Available data types from the `DataType` enum:

- `DataType.STRING`: For text values
- `DataType.INTEGER`: For whole numbers
- `DataType.FLOAT`: For decimal numbers
- `DataType.BOOLEAN`: For true/false values
- `DataType.JSON`: For structured data

### Advanced Plugin Example

<details>
<summary>Click to view advanced plugin example</summary>

```python
class CardmarketPricePlugin:
    """Plugin that extracts price information from Cardmarket pages."""
    
    # Global configuration flag to control whether prices are stored as floats or formatted strings
    STORE_PRICES_AS_FLOAT = False  # Set to True to store prices as float values without currency symbols
    
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
        Returns all possible fields this plugin can extract, with default values.
        """
        return [
            ScrapedField(
                name="card_name",
                value="Example Card",
                field_type=DataType.STRING,
                description="Name of the card",
                accumulate=True
            ),
            ScrapedField(
                name="card_set",
                value="Example Set",
                field_type=DataType.STRING,
                description="Set/expansion the card belongs to",
                accumulate=True
            ),
            ScrapedField(
                name="available_items",
                value=500,
                field_type=DataType.INTEGER,
                description="Number of available items for sale",
                accumulate=True
            ),
            ScrapedField(
                name="lowest_price",
                value=1.00 if self.STORE_PRICES_AS_FLOAT else "1,00 €",
                field_type=DataType.FLOAT if self.STORE_PRICES_AS_FLOAT else DataType.STRING,
                description="Lowest price available for the card",
                accumulate=True
            ),
            ScrapedField(
                name="card_rarity",
                value="Uncommon",
                field_type=DataType.STRING,
                description="Rarity of the card",
                accumulate=True
            )
        ]
        
    def _clean_price_string(self, price_string: str) -> str:
        """Clean and fix encoding issues in price strings."""
        if not price_string:
            return ""
            
        # Handle common encoding issues
        cleaned = price_string.replace("â‚¬", "€")
        cleaned = cleaned.replace("Â£", "£")
        cleaned = cleaned.replace("Â$", "$")
        
        # Remove any extra whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _parse_price_to_float(self, price_string: str) -> float:
        """Parse a price string into a float value, removing currency symbols."""
        if not price_string:
            return 0.0
            
        try:
            # Remove currency symbols and other non-numeric characters
            cleaned = ''.join(c for c in price_string if c.isdigit() or c in ',.').strip()
            
            # Handle European number format (comma as decimal separator)
            if ',' in cleaned and '.' in cleaned:
                # If both are present, assume European format with thousand separators
                cleaned = cleaned.replace('.', '')  # Remove thousand separators
                cleaned = cleaned.replace(',', '.')  # Convert decimal separator
            elif ',' in cleaned:
                # Only comma present, assume it's a decimal separator
                cleaned = cleaned.replace(',', '.')
                
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse(self, html: str) -> List[ScrapedField]:
        """Parse HTML content and extract Cardmarket price information."""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Extract card name and set
        try:
            title_container = soup.select_one('.page-title-container')
            if title_container:
                h1 = title_container.select_one('h1')
                if h1:
                    # Extract main card name (text before the span)
                    card_name = h1.get_text().strip()
                    set_span = h1.select_one('span')
                    if set_span:
                        card_name = card_name.replace(set_span.get_text(), '').strip()
                        card_set = set_span.get_text().strip()
                        
                        results.append(ScrapedField(
                            name="card_name",
                            value=card_name,
                            field_type=DataType.STRING,
                            description="Name of the card",
                            accumulate=True
                        ))
                        
                        results.append(ScrapedField(
                            name="card_set",
                            value=card_set,
                            field_type=DataType.STRING,
                            description="Set/expansion the card belongs to",
                            accumulate=True
                        ))
        except Exception:
            # Continue even if card name extraction fails
            pass
        
        # Find the info container
        container = soup.select_one('.info-list-container')
        if not container:
            return results
            
        # Process prices, rarity, etc.
        # ... (additional extraction code)
        
        return results
```
</details>

### Using Your Plugin

Once you've created your plugin:

1. Place the Python file in the `Backend/plugins` directory
2. Restart AutoScrape
3. Your plugin will be automatically loaded and available for use
4. When scraping a website, your plugin will process the HTML and save structured data

The extracted data from plugins is saved in the `Backend/scraped_data/` directory in CSV format.

## Why the cat
Isn't she adorable ?
