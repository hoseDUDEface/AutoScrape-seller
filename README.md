# AutoScrape

An automated scraper of a list of urls, with 10 different scraping technologies, and custom parsers as plugins in pythons.

## Disclaimer
This project was made using the infamous method of **vibe coding**, using Claude 3.7 . I understand most of it, but the javascript using [Ulixee Hero](https://github.com/ulixee/hero) is not something i'm comfortable with. I highly encourage anyone who wants to modify it to do so. If anyone wants to fork it and update it regularly, be my guest, and I'll reference you there.   
This software was tested on windows, and the behavior is currently unknown in any other OS. 

![image](https://github.com/user-attachments/assets/e77b06cf-c25f-49b1-a464-149fa0b7fa2d)


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
