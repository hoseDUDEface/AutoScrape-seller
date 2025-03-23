from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from selenium_stealth import stealth
from seleniumbase import Driver

def load_user_agents(filepath="user-agents.txt"):
    """Load user agents from a text file"""
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found. Using default user agent.")
        return ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"]
    
    with open(filepath, 'r') as file:
        user_agents = [line.strip() for line in file.readlines() if line.strip()]
    
    return user_agents

def setup_chrome_options(headless=False, user_agent=None):
    """Set up Chrome options with common settings for Cloudflare bypass"""
    options = webdriver.ChromeOptions()
    
    # Basic settings
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")
    
    # Apply user agent
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
    
    return options

def safe_scroll(driver, intensity="medium"):
    """Fast scroll with minimal delay - significantly shortened"""
    try:
        # Only do 1-2 scrolls no matter what intensity
        scroll_count = 1 if intensity == "low" else 2
        
        for _ in range(scroll_count):
            # Scroll down a bit
            driver.execute_script(f"window.scrollBy(0, {random.randint(200, 300)});")
            # Very short delay
            time.sleep(0.2)
    except Exception as e:
        print(f"Scrolling error: {str(e)}")

def safe_mouse_movements(driver, intensity="medium"):
    """Very quick mouse movements - significantly shortened"""
    try:
        # Only attempt 1 mouse movement
        elements = driver.find_elements(By.CSS_SELECTOR, "a, button")[:5]  # Limit search to first 5 elements
        visible_elements = [e for e in elements if e.is_displayed()]
        
        if visible_elements:
            actions = ActionChains(driver)
            try:
                # Move to one random element with minimal delay
                element = random.choice(visible_elements)
                actions.move_to_element(element).perform()
                time.sleep(0.2)
            except:
                pass
    except Exception as e:
        print(f"Mouse movement error: {str(e)}")

def add_human_behavior(driver, intensity="medium"):
    """Add very brief human-like behavior, completes in under 1 second"""
    # Only scroll for low intensity, do both for medium/high
    safe_scroll(driver, "low")  # Always use low intensity scrolling
    
    if intensity != "low":
        safe_mouse_movements(driver, "low")  # Always use low intensity mouse movements

def is_cloudflare_detected(driver):
    """Check if Cloudflare protection is detected"""
    cloudflare_indicators = [
        "Checking your browser before accessing",
        "Just a moment",
        "Please Wait... | Cloudflare",
        "DDoS protection by Cloudflare",
        "Please wait while we verify your browser"
    ]
    
    for indicator in cloudflare_indicators:
        if indicator in driver.page_source:
            print(f"⚠️ CloudFlare protection detected: '{indicator}'")
            return True
    return False

def wait_for_cloudflare(driver, timeout=5, headless=False):
    """Wait for Cloudflare challenge to be resolved - shorter timeout"""
    if not is_cloudflare_detected(driver):
        return True
        
    print(f"Waiting for CloudFlare challenge to resolve (up to {timeout} seconds)...")
    
    if headless:
        print("CloudFlare challenges typically fail in headless mode. Try with headless=False.")
        return False
    
    try:
        cloudflare_indicators = [
            "Checking your browser before accessing",
            "Just a moment",
            "Please Wait... | Cloudflare",
            "DDoS protection by Cloudflare",
            "Please wait while we verify your browser"
        ]
        
        WebDriverWait(driver, timeout).until(
            lambda d: not any(indicator in d.page_source for indicator in cloudflare_indicators)
        )
        print("CloudFlare challenge appears to be resolved!")
        return True
    except Exception as e:
        print(f"Timed out waiting for CloudFlare challenge: {str(e)}")
        return False

def create_driver_standard(headless=False):
    """Create a standard Selenium Chrome driver"""
    user_agents = load_user_agents()
    user_agent = random.choice(user_agents)
    options = setup_chrome_options(headless, user_agent)
    
    return webdriver.Chrome(options=options)

def create_driver_undetected(headless=False):
    """Create an undetected Chrome driver"""
    user_agents = load_user_agents()
    user_agent = random.choice(user_agents)
    
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={user_agent}")
    
    return uc.Chrome(options=options)

def create_driver_stealth(headless=False):
    """Create a Selenium driver with stealth mode"""
    user_agents = load_user_agents()
    user_agent = random.choice(user_agents)
    options = setup_chrome_options(headless)
    
    driver = webdriver.Chrome(options=options)
    
    # Apply stealth settings
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        user_agent=user_agent
    )
    
    return driver

def create_driver_seleniumbase(headless=False):
    """Create a SeleniumBase driver"""
    user_agents = load_user_agents()
    user_agent = random.choice(user_agents)
    options = setup_chrome_options(headless, user_agent)
    
    try:
        return Driver(uc=True, incognito=True, options=options)
    except Exception as e:
        print(f"Error creating SeleniumBase driver: {str(e)}")
        # Fallback to undetected_chromedriver
        print("Falling back to undetected_chromedriver...")
        return create_driver_undetected(headless)

def get_html_with_driver(driver, url, headless=False, human_behavior=True, behavior_intensity="medium"):
    """Fetch HTML source from a website with the given driver"""
    try:
        print(f"Navigating to: {url}")
        driver.get(url)
        
        if human_behavior:
            add_human_behavior(driver, behavior_intensity)
            
        # Check for Cloudflare and return None if detected and not bypassed
        if is_cloudflare_detected(driver):
            if not wait_for_cloudflare(driver, 5, headless):  # Reduced timeout
                print("Cloudflare challenge not bypassed, returning None")
                html_source = None
            else:
                # Cloudflare was bypassed successfully
                html_source = driver.page_source
        else:
            # No Cloudflare detected
            html_source = driver.page_source
            
        return html_source, driver
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        driver.quit()
        return None, None

def getHtmlAdvanced(url, method="undetected", headless=False, human_behavior=True, behavior_intensity="medium", auto_close_driver=True):
    """
    Extract HTML source using the specified method, returns None if Cloudflare is detected
    
    Args:
        url: URL to scrape
        method: Method to use (undetected, stealth, standard, seleniumbase)
        headless: Whether to run in headless mode
        human_behavior: Whether to simulate human behavior
        behavior_intensity: Intensity of human behavior (low, medium, high)
        auto_close_driver: Whether to automatically close the driver after scraping
        
    Returns:
        HTML source (or None if Cloudflare is detected)
    """
    driver = None
    try:
        # Create the appropriate driver based on method
        if method == "undetected":
            driver = create_driver_undetected(headless)
            method_name = "Undetected ChromeDriver"
        elif method == "stealth":
            driver = create_driver_stealth(headless)
            method_name = "Stealth mode"
        elif method == "seleniumbase":
            driver = create_driver_seleniumbase(headless)
            method_name = "SeleniumBase"
        else:  # standard
            driver = create_driver_standard(headless)
            method_name = "Standard Selenium"
        
        print(f"Created driver using {method_name}")
        
        # Navigate to the URL
        print(f"Navigating to: {url}")
        driver.get(url)
        
        # Add human-like behavior if requested
        if human_behavior:
            add_human_behavior(driver, behavior_intensity)
            
        # Check for Cloudflare
        if is_cloudflare_detected(driver):
            if not wait_for_cloudflare(driver, 5, headless):  # Reduced timeout
                print("Cloudflare challenge not bypassed, returning None")
                return None
        
        # No Cloudflare detected or it was bypassed successfully
        html_source = driver.page_source
        return html_source
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return None
    finally:
        # Close the driver if auto_close_driver is True
        if driver and auto_close_driver:
            try:
                driver.quit()
                print("Driver closed")
            except Exception as e:
                print(f"Error closing driver: {str(e)}")