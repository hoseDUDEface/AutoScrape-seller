#!/usr/bin/env python3
"""
Cloudflare Bypass Scraper - Python wrapper for JavaScript-based browser automation
Uses multiple engines (Hero, Puppeteer, Puppeteer-Extra, Puppeteer-Stealth) to bypass protection
"""

import subprocess
import os
import json
import tempfile
import time
import argparse
import sys
from typing import Optional, Dict, Any, Union

def scrape_with_js(
    url: str, 
    engine: str = 'hero', 
    headless: bool = True, 
    timeout: int = 60000, 
    output_file: Optional[str] = None,
    wait_for_selector: Optional[str] = None,
    proxy_url: Optional[str] = None,
    user_agent: Optional[str] = None,
    cookies: Optional[list] = None,
    debug_screenshots: bool = False,
    debug_output: bool = False,
    fast_mode: bool = True 
) -> str:
    """
    Scrape a URL using the JavaScript-based browser automation
    
    Args:
        url: The URL to scrape
        engine: Browser engine to use ('hero', 'puppeteer', 'puppeteer-extra', 'puppeteer-stealth')
        headless: Whether to run in headless mode
        timeout: Timeout in milliseconds
        output_file: File to save the HTML output to
        wait_for_selector: CSS selector to wait for before returning HTML
        proxy_url: Proxy URL to use (e.g., 'http://user:pass@host:port')
        user_agent: User agent string to use (if None, a random one will be used)
        cookies: List of cookies to set
        debug_screenshots: Whether to save screenshots for debugging
        debug_output: Whether to print debug output
        fast_mode: Enable fast mode for 2-5x faster scraping
    
    Returns:
        HTML content of the page
    """
    valid_engines = ['hero', 'puppeteer', 'puppeteer-extra', 'puppeteer-stealth']
    if engine not in valid_engines:
        raise ValueError(f"Engine must be one of: {', '.join(valid_engines)}")
    
    # Ensure hero.js exists
    js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hero.js')
    if not os.path.exists(js_path):
        raise FileNotFoundError(
            f"JavaScript scraper not found at: {js_path}\n"
            f"Make sure to save the JavaScript code as 'hero.js' in the same directory."
        )
    
    # Create configuration to pass to the JS script
    config = {
        "url": url,
        "engine": engine,
        "headless": headless,
        "timeout": timeout,
        "debugScreenshots": debug_screenshots,
        "fastMode": fast_mode  # Add fast mode to config
    }
    
    # Add optional parameters if provided
    if wait_for_selector:
        config["waitForSelector"] = wait_for_selector
    if proxy_url:
        config["proxyUrl"] = proxy_url
    if user_agent:
        config["userAgent"] = user_agent
    if cookies:
        config["cookies"] = cookies
    
    # Create a temporary file for the configuration
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as config_file:
        json.dump(config, config_file)
        config_path = config_file.name
    
    # Prepare command
    command = ['node', js_path, '--config', config_path]
    
    try:
        start_time = time.time()
        if debug_output:
            print(f"Scraping {url} with {engine} engine" + (" (fast mode)" if fast_mode else ""))
            print(f"Configuration: {json.dumps(config, indent=2)}")
        
        # Run the JavaScript scraper
        process = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        
        # Remove the temporary config file
        try:
            os.unlink(config_path)
        except Exception as e:
            if debug_output:
                print(f"Warning: Failed to delete temporary config file: {e}")
        
        # Check for errors
        if process.returncode != 0:
            error_msg = process.stderr
            raise RuntimeError(f"Scraping failed: {error_msg}")
        
        # Get the HTML from stdout
        html = process.stdout
        
        # Log any stderr output if in debug mode
        if debug_output and process.stderr:
            print("Debug output from JavaScript:")
            print(process.stderr)
        
        # Save to output file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            if debug_output:
                print(f"HTML saved to {output_file}")
        
        elapsed_time = time.time() - start_time
        if debug_output:
            print(f"Scraping completed in {elapsed_time:.2f} seconds")
            print(f"HTML size: {len(html)} bytes")
        
        return html
        
    except subprocess.CalledProcessError as e:
        print(f"Error running JavaScript scraper: {e}")
        print(f"stderr: {e.stderr}")
        raise RuntimeError(f"Scraping failed: {e.stderr}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        # Ensure we clean up the config file
        if os.path.exists(config_path):
            try:
                os.unlink(config_path)
            except:
                pass

def main():
    """Command line interface for the scraper"""
    parser = argparse.ArgumentParser(description='Scrape a website using various browser engines with Cloudflare bypass')
    parser.add_argument('url', help='URL to scrape')
    parser.add_argument('--engine', '-e', choices=['hero', 'puppeteer', 'puppeteer-extra', 'puppeteer-stealth'], 
                      default='hero', help='Browser engine to use (default: hero)')
    parser.add_argument('--visible', '-v', action='store_true', help='Show browser window (non-headless mode)')
    parser.add_argument('--output', '-o', help='Output file for HTML')
    parser.add_argument('--timeout', '-t', type=int, default=60000, help='Timeout in milliseconds (default: 60000)')
    parser.add_argument('--wait-for', '-w', help='CSS selector to wait for before returning HTML')
    parser.add_argument('--proxy', '-p', help='Proxy URL to use (e.g., http://user:pass@host:port)')
    parser.add_argument('--user-agent', '-u', help='User agent string to use')
    parser.add_argument('--debug-screenshots', '-s', action='store_true', help='Save screenshots for debugging')
    parser.add_argument('--debug', '-d', action='store_true', help='Show debug output')
    parser.add_argument('--fast', '-f', action='store_true', help='Enable fast mode (2-5x faster)')
    
    args = parser.parse_args()
    
    try:
        html = scrape_with_js(
            url=args.url,
            engine=args.engine,
            headless=not args.visible,
            timeout=args.timeout,
            output_file=args.output,
            wait_for_selector=args.wait_for,
            proxy_url=args.proxy,
            user_agent=args.user_agent,
            debug_screenshots=args.debug_screenshots,
            debug_output=args.debug,
            fast_mode=args.fast  # Pass the fast mode parameter
        )
        
        if not args.output:
            # If not saving to a file, output the first part of the HTML
            preview_length = 500 if not args.debug else 1000
            preview = html[:preview_length] + ("..." if len(html) > preview_length else "")
            print(f"HTML length: {len(html)} characters")
            print(preview)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()