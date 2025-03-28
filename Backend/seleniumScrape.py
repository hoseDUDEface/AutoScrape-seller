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
        options.add_argument("--headless")
        options.headless = True
    else :
         options.headless = False
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
    """Create a SeleniumBase driver with better Cloudflare bypass capabilities"""
    # Note: SeleniumBase's Driver handles many settings internally when uc=True
    try:
        # For best Cloudflare bypass, use uc=True for undetected-chromedriver features
        # headless=False is strongly recommended for Cloudflare bypass
        return Driver(uc=True, incognito=True, headless=headless)
    except Exception as e:
        print(f"Error creating SeleniumBase driver: {str(e)}")
        # Fallback to undetected_chromedriver
        print("Falling back to undetected_chromedriver...")
        return create_driver_undetected(headless)

def bypass_cloudflare_with_seleniumbase(url, headless=False, reconnect_time=6):
    """
    Use SeleniumBase's specialized methods to bypass Cloudflare protection
    
    Args:
        url: URL to scrape
        headless: Whether to run in headless mode (not recommended for Cloudflare bypass)
        reconnect_time: Time to reconnect, giving browser time to handle JS challenge
        
    Returns:
        Tuple of (HTML source, driver) or (None, driver) if failed
    """
    driver = None
    try:
        # Create the SeleniumBase driver - recommend GUI mode for Cloudflare
        driver = Driver(uc=True, headless=headless)
        print(f"Created SeleniumBase driver with UC mode enabled")
        
        # Use the specialized method for opening with reconnect time
        print(f"Opening {url} with reconnect time of {reconnect_time} seconds")
        driver.uc_open_with_reconnect(url, reconnect_time=reconnect_time)
        
        # Try to click the CAPTCHA checkbox if it appears
        # Note: This only works in GUI mode (non-headless)
        if not headless:
            try:
                print("Attempting to click CAPTCHA checkbox if present")
                driver.uc_gui_click_captcha()
            except Exception as e:
                print(f"No CAPTCHA found or error clicking it: {str(e)}")
        
        # Check if we successfully bypassed Cloudflare
        if is_cloudflare_detected(driver):
            print("Failed to bypass Cloudflare challenge")
            return None, driver
        
        # Successfully bypassed - return the HTML
        html_source = driver.page_source
        print("Successfully obtained page content after Cloudflare")
        return html_source, driver
        
    except Exception as e:
        print(f"Error during Cloudflare bypass: {str(e)}")
        return None, driver

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
        if driver:
            driver.quit()
        return None, None

def getHtmlAdvanced(url, method="seleniumbase", headless=False, human_behavior=True, 
                    behavior_intensity="medium", auto_close_driver=True, reconnect_time=6):
    """
    Extract HTML source using the specified method, with improved Cloudflare bypass
    
    Args:
        url: URL to scrape
        method: Method to use (undetected, stealth, standard, seleniumbase)
        headless: Whether to run in headless mode
        human_behavior: Whether to simulate human behavior
        behavior_intensity: Intensity of human behavior (low, medium, high)
        auto_close_driver: Whether to automatically close the driver after scraping
        reconnect_time: For seleniumbase method, time to reconnect for JS challenge
        
    Returns:
        HTML source (or None if Cloudflare is detected and not bypassed)
    """
    driver = None
    try:
        # If using SeleniumBase with its specialized Cloudflare bypass methods
        if method == "seleniumbase":
            print("Using SeleniumBase with specialized Cloudflare bypass methods")
            html, driver = bypass_cloudflare_with_seleniumbase(url, headless, reconnect_time)
            if html:
                print("Successfully bypassed Cloudflare using SeleniumBase specialized methods")
                return html
            else:
                print("SeleniumBase specialized methods failed to bypass Cloudflare")
                # Fall through to try standard approach
        
        # Create the appropriate driver based on method
        if method == "undetected":
            driver = create_driver_undetected(headless)
            method_name = "Undetected ChromeDriver"
        elif method == "stealth":
            driver = create_driver_stealth(headless)
            method_name = "Stealth mode"
        elif method == "seleniumbase":
            # This would be a fallback if the specialized method failed
            driver = create_driver_seleniumbase(headless)
            method_name = "SeleniumBase (standard approach)"
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
        print("Successfully obtained page content")
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

def interact_with_captcha(driver):
    """
    Attempt to identify and solve a CAPTCHA if present.
    Supports multiple CAPTCHA types including Cloudflare's checkbox challenge.
    """
    try:
        # Try SeleniumBase's built-in CAPTCHA clicker if available
        if hasattr(driver, 'uc_gui_click_captcha'):
            print("Using SeleniumBase's built-in CAPTCHA clicker")
            driver.uc_gui_click_captcha()
            return True
            
        # Look for common CAPTCHA elements
        # Cloudflare checkbox
        cf_checkbox = driver.find_elements(By.CSS_SELECTOR, 
                                         "input[type='checkbox'], .recaptcha-checkbox")
        
        if cf_checkbox:
            for checkbox in cf_checkbox:
                if checkbox.is_displayed() and checkbox.is_enabled():
                    print("Found CAPTCHA checkbox, attempting to click")
                    checkbox.click()
                    time.sleep(2)  # Wait for any animations or verifications
                    return True
        
        # Look for iframe-based CAPTCHAs (like reCAPTCHA)
        captcha_frames = driver.find_elements(By.CSS_SELECTOR, 
                                            "iframe[src*='recaptcha'], iframe[src*='captcha']")
        
        if captcha_frames:
            print("Found CAPTCHA iframe, attempting to switch and interact")
            for frame in captcha_frames:
                if frame.is_displayed():
                    # Switch to the frame
                    driver.switch_to.frame(frame)
                    
                    # Look for checkbox inside frame
                    checkbox = driver.find_elements(By.CSS_SELECTOR, 
                                                 ".recaptcha-checkbox-border")
                    if checkbox:
                        for cb in checkbox:
                            if cb.is_displayed() and cb.is_enabled():
                                cb.click()
                                time.sleep(2)
                                driver.switch_to.default_content()
                                return True
                    
                    # Switch back to main content
                    driver.switch_to.default_content()
        
        print("No CAPTCHA elements identified or interaction failed")
        return False
        
    except Exception as e:
        print(f"Error during CAPTCHA interaction: {str(e)}")
        return False
        
# Example usage
if __name__ == "__main__":
    # Example 1: Using the improved SeleniumBase method
    url = "https://example.com"  # Replace with your target URL
    
    print("Testing SeleniumBase with Cloudflare bypass...")
    html = getHtmlAdvanced(
        url=url, 
        method="seleniumbase",
        headless=False,  # Recommend False for Cloudflare bypass
        reconnect_time=6
    )
    
    if html:
        print("Successfully retrieved HTML content")
        print(f"HTML length: {len(html)} characters")
    else:
        print("Failed to retrieve HTML content")