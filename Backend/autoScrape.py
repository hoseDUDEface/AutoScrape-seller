import sys
import os
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_path)
from PyQt5.QtWidgets import QApplication, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal
from seleniumScrape import getHtmlAdvanced, create_driver_undetected, create_driver_stealth, create_driver_standard, create_driver_seleniumbase
from scraper_gui import DarkThemeApp
from heroPy import scrape_with_js
from enum import Enum, auto

class ScraperWorker(QThread):
    url_status = pyqtSignal(int, str)  # Signal for URL status: 0=success, 1=warning, 2=error
    finished = pyqtSignal()           # Signal for completion notification
    remove_url = pyqtSignal(str)      # Signal to remove a successful URL from the input box
    suspend_execution = pyqtSignal(int, str)  # Signal to suspend execution with timeout and reason
    plugin_results = pyqtSignal(list)  # Signal to send plugin results to the app
    
    def __init__(self, options, urls, timeout_value):
        super().__init__()
        self.options = options
        self.urls = urls
        self.stop_execution = False    # Flag to stop execution completely
        self.is_suspended = False      # Flag to suspend execution temporarily
        self.timeout_seconds = timeout_value  # Timeout value in seconds
        
    def run(self):
        """Main execution method for the worker thread"""
        try:
            # Process headless selection
            headless = self.options["Headless"] == "true"
            
            # Check which mode to use - Playwright, Ulixee Hero or Selenium
            playwright_mode = self.options.get("Playwright")
            
            if playwright_mode in ["standard", "puppeteer +stealth"]:
                # Map the UI selection to the engine parameter
                engine = "playwright" if playwright_mode == "standard" else "playwright-stealth"
                print(f"\n> Using Playwright ({playwright_mode})")
                self.process_urls_with_playwright(self.urls, engine, headless)
            else:
                # Check Ulixee Hero modes
                hero_mode = self.options["Ulixee Hero Mode"]
                if hero_mode == "standard":
                    # Use Ulixee Hero
                    print(f"\n> Using Ulixee Hero")
                    self.process_urls_with_hero(self.urls, headless)
                elif hero_mode == "puppeteer":
                    # Use Puppeteer
                    print(f"\n> Using Puppeteer")
                    self.process_urls_with_puppeteer(self.urls, "puppeteer", headless)
                elif hero_mode == "<- extra":
                    # Use Puppeteer Extra
                    print(f"\n> Using Puppeteer Extra")
                    self.process_urls_with_puppeteer(self.urls, "puppeteer-extra", headless)
                elif hero_mode == "<- +stealth":
                    # Use Puppeteer Extra with Stealth
                    print(f"\n> Using Puppeteer Extra + Stealth")
                    self.process_urls_with_puppeteer(self.urls, "puppeteer-stealth", headless)
                else:
                    # Use Selenium
                    selenium_mode = self.options["Selenium Mode"].lower()
                    human_behavior = self.options["Human Behavior"] == "true"
                    behavior_intensity = self.options["Behavior Intensity"].lower() if human_behavior else "medium"
                    
                    print(f"\n> Using Selenium ({selenium_mode})")
                    self.process_urls_with_selenium(self.urls, selenium_mode, headless, human_behavior, behavior_intensity)
        except Exception as e:
            print(f"\n> Error in worker thread: {str(e)}")
        finally:
            self.finished.emit()
    
    def is_cloudflare_detection_page(self, html_content):
        # Convert to lowercase for case-insensitive matching
        html_lower = html_content.lower()
        
        # More comprehensive set of Cloudflare indicators
        cloudflare_indicators = [
            # Title and meta indicators
            "<title>just a moment...</title>",
            '<meta name="robots" content="noindex,nofollow"',
            '<meta http-equiv="refresh" content="390"',  # Common timeout refresh
            
            # Common element IDs and classes
            'class="loading-spinner"',
            'class="lds-ring"',
            'class="main-wrapper"',
            'class="challenge-',
            'id="challenge-error-text"',
            'id="challenge-success-text"',
            
            # Common text phrases unique to Cloudflare
            "verifying you are human",
            "this may take a few seconds",
            "needs to review the security of your connection",
            "enable javascript and cookies to continue",
            "waiting for",
            "to respond",
            "verification successful",
            "performance & security by",
            "ray id:",
            
            # Cloudflare-specific script and resource references
            "/cdn-cgi/challenge-platform/",
            "/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page",
            "cloudflare",
            "cloudflareinsights.com/beacon",
            "cf_chl_opt",
            "cf-ray",
            "cf_chl_",
            "chl_page",
            
            # Function calls and JS specific to Cloudflare
            "turnstile",
            "challenges.cloudflare.com",
            "window._cf_chl_opt",
            "cOgUHash",
            "cOgUQuery",
            
            # Visual elements unique to Cloudflare
            'div class="lds-ring"><div></div><div></div><div></div><div></div></div>',
            'background-image:url(data:image/svg+xml;base64,',  # SVG base64 icons
            
            # Specific CSS patterns
            "@keyframes lds-ring{",
            "animation:lds-ring",
            
            # Footer elements
            'role="contentinfo"',
            '<a rel="noopener noreferrer" href="https://www.cloudflare.com?utm_source=challenge',

            # Previously strong elements
            "ray id: <code>",
            'class="ray-id">ray id:',
            '/cdn-cgi/challenge-platform/'
        ]
        
        # Strong indicators that, if any are present, almost certainly indicate a Cloudflare page
        strong_indicators = [
            "window._cf_chl_opt",
            "cloudflare.com?utm_source=challenge",
            "challenge-platform/h/b/orchestrate/chl_page"
        ]
        
        # Check if any strong indicators are present
        for indicator in strong_indicators:
            if indicator in html_lower:
                print(f"Strong Cloudflare indicator found: {indicator}")
                return True
        
        # Count how many general indicators are found
        indicators_found = sum(1 for indicator in cloudflare_indicators if indicator in html_lower)
        
        # We require a higher threshold for confidence (65% of indicators)
        threshold = int(len(cloudflare_indicators) * 0.65)
        
        print(f"Cloudflare indicators found: {indicators_found}/{len(cloudflare_indicators)}")
        
        return indicators_found >= threshold
    
    def process_urls_with_playwright(self, urls, engine_type, headless):
        """Process URLs using Playwright variants"""
        from playwrightPy import scrape_with_playwright_sync  # Import from your paste.txt file
        
        for i, url in enumerate(urls, 1):
            if self.stop_execution:
                print(f"\n> Execution stopped permanently")
                break
                
            # Check if execution is suspended
            while self.is_suspended:
                # Wait while suspended (check every 100ms)
                self.msleep(100)
                
            print(f"\n> [{i}/{len(urls)}] Processing with Playwright ({engine_type}): {url}")
            
            try:
                html = scrape_with_playwright_sync(
                    url=url, 
                    engine=engine_type, 
                    headless=headless
                )
                self.process_html(html, url, i)
            except Exception as e:
                print(f"> Error: {str(e)}")
                # Report error in process_html with None
                self.process_html(None, url, i)

    def process_urls_with_hero(self, urls, headless):
        """Process URLs using Ulixee Hero"""
        from heroPy import scrape_with_js
        
        for i, url in enumerate(urls, 1):
            if self.stop_execution:
                print(f"\n> Execution stopped permanently")
                break
                
            # Check if execution is suspended
            while self.is_suspended:
                # Wait while suspended (check every 100ms)
                self.msleep(100)
                
            print(f"\n> [{i}/{len(urls)}] Processing with Ulixee Hero: {url}")
            
            try:
                html = scrape_with_js(url=url, engine="hero", headless=headless)
                self.process_html(html, url, i)
            except Exception as e:
                print(f"> Error: {str(e)}")
                # Report error in process_html with None
                self.process_html(None, url, i)
    
    def process_urls_with_puppeteer(self, urls, engine_type, headless):
        """Process URLs using Puppeteer variants"""
        from heroPy import scrape_with_js
        
        for i, url in enumerate(urls, 1):
            if self.stop_execution:
                print(f"\n> Execution stopped permanently")
                break
                
            # Check if execution is suspended
            while self.is_suspended:
                # Wait while suspended (check every 100ms)
                self.msleep(100)
                
            print(f"\n> [{i}/{len(urls)}] Processing with {engine_type}: {url}")
            
            try:
                html = scrape_with_js(url=url, engine=engine_type, headless=headless)
                self.process_html(html, url, i)
            except Exception as e:
                print(f"> Error: {str(e)}")
                # Report error in process_html with None
                self.process_html(None, url, i)
    
    def process_urls_with_selenium(self, urls, method, headless, human_behavior, behavior_intensity):
        """Process URLs using a single Selenium driver instance"""
        from seleniumScrape import create_driver_undetected, create_driver_stealth, create_driver_seleniumbase, create_driver_standard
        
        # Create the driver first
        print(f"\n> Creating driver ({method})...")
        
        driver = None
        try:
            # Create the appropriate driver based on method
            if method == "undetected":
                driver = create_driver_undetected(headless)
            elif method == "stealth":
                driver = create_driver_stealth(headless)
            elif method == "base":
                driver = create_driver_seleniumbase(headless)
            else:  # standard
                driver = create_driver_standard(headless)
                
            print("> Driver created successfully")
            
            # Process each URL
            for i, url in enumerate(urls, 1):
                if self.stop_execution:
                    print(f"\n> Execution stopped permanently")
                    break
                    
                # Check if execution is suspended
                while self.is_suspended:
                    # Wait while suspended (check every 100ms)
                    self.msleep(100)
                    
                print(f"\n> [{i}/{len(urls)}] Processing: {url}")
                
                try:
                    # Use driver.get directly
                    print("> Navigating to URL...")
                    driver.get(url)
                    
                    # Apply human behavior if enabled
                    if human_behavior:
                        print(f"> Applying human behavior ({behavior_intensity})...")
                        from seleniumScrape import add_human_behavior
                        add_human_behavior(driver, behavior_intensity)
                    
                    # Get page source
                    html = driver.page_source
                    self.process_html(html, url, i)
                        
                except Exception as e:
                    print(f"> Error processing URL: {str(e)}")
                    # Report error in process_html with None
                    self.process_html(None, url, i)
                    
            print("\n> All URLs processed successfully")
                
        except Exception as e:
            print(f"\n> Error creating driver: {str(e)}")
        finally:
            # Close the driver
            if driver:
                try:
                    print("\n> Closing browser...")
                    driver.quit()
                    print("> Browser closed")
                except Exception as e:
                    print(f"> Error closing browser: {str(e)}")
    

    def process_html(self, html, url, index):
        """Process HTML content that was scraped and emit appropriate status signal"""
        import csv
        import time
        import os
        
        # CSV file handling - create the CSV file if it doesn't exist yet
        if not hasattr(self, 'csv_filename'):
            # Get the current unix timestamp
            timestamp = int(time.time())
            
            # Get the selected plugin name
            app = QApplication.instance()
            plugin_name = "no_plugin"
            for widget in app.topLevelWidgets():
                if isinstance(widget, ScraperApp):
                    if widget.selected_plugin != "Download HTML":
                        plugin_name = os.path.splitext(widget.selected_plugin)[0]
                    break
            
            # Create the CSV filename
            self.csv_filename = f"{timestamp}_{plugin_name}.csv"
            self.csv_header_written = False
            
            # Create output directory if it doesn't exist
            csv_dir = "scraped_data"
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir)
                
            self.csv_path = os.path.join(csv_dir, self.csv_filename)
            print(f"> CSV output will be saved to: {self.csv_path}")
        
        # First determine status
        if html is None:
            # HTML is None, this is an error
            print(f"> Error: No HTML content retrieved for {url}")
            self.url_status.emit(2, url)
            # Suspend execution on error
            self.suspend_execution.emit(self.timeout_seconds, "Error: Failed to retrieve content")
            self.is_suspended = True
            return
            
        # Check if this is a Cloudflare page
        if self.is_cloudflare_detection_page(html):
            print(f"> Cloudflare detection page found for {url}")
            self.url_status.emit(1, url)
            # Suspend execution on warning
            self.suspend_execution.emit(self.timeout_seconds, "Warning: Cloudflare protection detected")
            self.is_suspended = True
            return
        
        # Check for HTTP 429 response
        if "HTTP ERROR 429" in html or "Too Many Requests" in html:
            print(f"> HTTP 429 Too Many Requests error for {url}")
            self.url_status.emit(1, url)  # Using warning status for rate limiting
            # Suspend execution to prevent further rate limiting
            self.suspend_execution.emit(self.timeout_seconds, "Warning: Rate limit (HTTP 429) detected")
            self.is_suspended = True
            return
                
        # If we got here, it's a successful retrieval
        print(f"> Success! Retrieved {len(html)} characters of HTML")
        
        # Apply the selected plugin if not in "Download HTML" mode
        app = QApplication.instance()
        main_window = None
        
        # Find the main window
        for widget in app.topLevelWidgets():
            if isinstance(widget, ScraperApp):
                main_window = widget
                break
                
        if main_window and main_window.selected_plugin != "Download HTML":
            try:
                # Import the selected plugin
                import importlib.util
                import sys
                # Import here explicitly to avoid scope issues
                import os as os_module
                from enum import Enum, auto
                
                plugins_dir = os.path.abspath("./Plugins/")
                plugin_path = os.path.join(plugins_dir, main_window.selected_plugin)
                
                print(f"> Loading plugin: {plugin_path}")
                
                # Add Plugins directory to Python path temporarily to help with imports
                if plugins_dir not in sys.path:
                    sys.path.insert(0, plugins_dir)
                
                # Copy templated_plugin.py contents for any plugin that needs it
                # This defines the needed classes in memory
                if "templated_plugin" not in sys.modules:
                    try:
                        # Define DataType enum and ScrapedField class directly
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

                        class ScrapedField:
                            """Represents a single piece of data extracted from HTML."""
                            def __init__(self, name, value, field_type, found=True, description=None, accumulate=False):
                                self.name = name
                                self.value = value
                                self.field_type = field_type
                                self.found = found
                                self.description = description
                                self.accumulate = accumulate
                        
                        # Create a fake module to provide these classes to the plugins
                        class FakeModule:
                            pass
                        
                        fake_templated_plugin = FakeModule()
                        fake_templated_plugin.DataType = DataType
                        fake_templated_plugin.ScrapedField = ScrapedField
                        
                        # Add to sys.modules
                        sys.modules['templated_plugin'] = fake_templated_plugin
                        
                        print("> Created templated_plugin module in memory")
                    except Exception as e:
                        print(f"> Error creating templated_plugin module: {str(e)}")
                
                # Load the module
                spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
                if spec is None:
                    print(f"> Error: Could not find plugin at {plugin_path}")
                else:
                    plugin_module = importlib.util.module_from_spec(spec)
                    sys.modules["plugin_module"] = plugin_module  # Add to sys.modules for imports to work
                    spec.loader.exec_module(plugin_module)
                    
                    # Find the plugin class in the module
                    # We're looking for a class that inherits from ScraperPlugin or DataAnalysisPlugin
                    plugin_class = None
                    for name, obj in plugin_module.__dict__.items():
                        if isinstance(obj, type) and hasattr(obj, 'parse') and callable(obj.parse):
                            plugin_class = obj
                            break
                    
                    if plugin_class:
                        print(f"> Found plugin class: {plugin_class.__name__}")
                        
                        # Create an instance and parse the HTML
                        plugin_instance = plugin_class()
                        parsed_results = plugin_instance.parse(html)
                        
                        print(f"\n> Plugin results for {url}:")
                        for field in parsed_results:
                            print(f"  {field.name}: {field.value}" + 
                                (f" ({field.description})" if field.description else ""))
                        
                        # Emit the results to the app
                        self.plugin_results.emit(parsed_results)
                        
                        # Write results to CSV
                        try:
                            # Prepare data for CSV - include URL for reference
                            csv_row = {'url': url}
                            
                            # Add all fields to the row
                            for field in parsed_results:
                                # Convert the value to string if it's not
                                if field.value is not None:
                                    csv_row[field.name] = str(field.value)
                                else:
                                    csv_row[field.name] = ""
                            
                            # Get all field names for header
                            field_names = ['url'] + [field.name for field in parsed_results]
                            
                            # Write to CSV file
                            with open(self.csv_path, mode='a', newline='', encoding='utf-8') as csv_file:
                                writer = csv.DictWriter(csv_file, fieldnames=field_names)
                                
                                # Write header if this is the first time
                                if not self.csv_header_written:
                                    writer.writeheader()
                                    self.csv_header_written = True
                                
                                # Write the data row
                                writer.writerow(csv_row)
                            
                            print(f"> CSV data saved to: {self.csv_path}")
                        except Exception as csv_e:
                            print(f"> Error saving to CSV: {str(csv_e)}")
                        
                    else:
                        print(f"> Error: Could not find plugin class in {plugin_path}")
                    
                    # Clean up - remove our module to avoid conflicts
                    if "plugin_module" in sys.modules:
                        del sys.modules["plugin_module"]
            except Exception as e:
                print(f"> Error applying plugin: {str(e)}")
                import traceback
                traceback.print_exc()  # Print full traceback for debugging
        
        try:
            # Import os explicitly to avoid scope issues
            import os as os_module
            
            # Create output directory if it doesn't exist
            output_dir = "scraped_html"
            if not os_module.path.exists(output_dir):
                os_module.makedirs(output_dir)
                    
            # Create a safe filename from the URL
            safe_filename = url.replace("http://", "").replace("https://", "")
            safe_filename = safe_filename.replace("/", "_").replace(":", "_")
            if len(safe_filename) > 50:
                safe_filename = safe_filename[:50]
            safe_filename = f"{safe_filename}_{index}.html"
            
            # Save the file
            file_path = os_module.path.join(output_dir, safe_filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"> HTML saved to: {file_path}")
            
            # Emit success signal
            self.url_status.emit(0, url)
            
            # Signal to remove this URL from the input
            self.remove_url.emit(url)
            
        except Exception as e:
            print(f"> Error saving HTML: {str(e)}")
            # Error saving the file is still an error
            self.url_status.emit(2, url)
            # Stop execution on error
            self.stop_execution = True

class ScraperApp(DarkThemeApp):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Scraper v0.1")
        
        # Add worker attribute
        self.worker = None
        self.is_scraping = False
        
        # Initialize counters for each URL type
        self.success_count = 0
        self.warning_count = 0
        self.error_count = 0
        
        # Initialize dictionary to store accumulated results
        self.accumulated_results = {}
        
        # Initialize total URLs count
        self.total_urls = 0

        # Load files
        self.browse_button.clicked.disconnect()
        self.browse_button.clicked.connect(self.load_url_list)
        # Run button
        self.run_button.clicked.disconnect()  # Disconnect any previous connections
        self.run_button.clicked.connect(self.run_scraper)
        # every other button is a good looking radio button grid
        

    def get_file_dialog(self):
        """Returns an instance of QFileDialog"""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        return dialog
    
    def load_url_list(self):
        """Load a list of URLs from a file into the textbox"""
        file_path, _ = self.get_file_dialog().getOpenFileName(
            self, "Select URL List File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    # Read all lines from the file
                    urls = file.readlines()
                    
                    # Process URLs - remove commas at the end and strip whitespace
                    processed_urls = []
                    for url in urls:
                        url = url.strip()
                        if url.endswith(','):
                            url = url[:-1]
                        if url:  # Only add non-empty URLs
                            processed_urls.append(url)
                    
                    # Set the processed URLs to the text box
                    self.file_path_input.setText('\n'.join(processed_urls))
                    
            except Exception as e:
                self.show_message_dialog(f"> Error loading file: {str(e)}")
    
    def run_scraper(self):
        """Run the scraping process using a worker thread"""
        # Check if already running
        if self.is_scraping:
            return
            
        # Reset counters for a new run
        self.success_count = 0
        self.warning_count = 0
        self.error_count = 0
        
        # Clear accumulated results for a new run
        self.accumulated_results = {}
        
        # Clear the results table
        self.results_table.setRowCount(0)
            
        # Get all the selected options
        options = {k: v for k, v in self.selected_buttons.items()}
        
        # Store the selected plugin
        self.selected_plugin = self.plugin_dropdown.currentText()
        
        # Disable the plugin dropdown during scraping
        self.plugin_dropdown.setEnabled(False)
        
        # Get URLs from the text edit
        urls_text = self.file_path_input.toPlainText().strip()
        if not urls_text:
            return
            
        # Split into individual URLs
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # Set total URLs count
        self.total_urls = len(urls)
        
        # Update the counter
        self.update_done_total_counter()
        
        # Get timeout value from the spinbox
        timeout_seconds = self.timeout_value.value()
        
        # Create and configure the worker
        self.worker = ScraperWorker(options, urls, timeout_seconds)
        
        # Connect signals
        self.worker.url_status.connect(self.handle_url_status)
        self.worker.finished.connect(self.scraping_finished)
        self.worker.remove_url.connect(self.remove_url_from_input)
        self.worker.suspend_execution.connect(self.show_suspension_timer)
        self.worker.plugin_results.connect(self.handle_plugin_results)  # Connect the new signal
        
        # Update UI state
        self.is_scraping = True
        self.run_button.setEnabled(False)
        self.run_button.setText("RUNNING...")
        self.cancel_button.setVisible(True)  # Show cancel button
        
        # Start the worker thread
        self.worker.start()
    
    def handle_plugin_results(self, results):
        """Handle the plugin results received from the worker thread"""
        # Update accumulated results
        for field in results:
            field_name = field.name
            field_value = field.value
            
            # Get the type name as a string for comparison
            field_type_name = field.field_type.name if hasattr(field.field_type, 'name') else str(field.field_type)
            
            # Handle accumulation for numeric fields - check the field type name
            if hasattr(field, 'accumulate') and field.accumulate and field_type_name in ['INTEGER', 'FLOAT']:
                # Convert value to float or int if needed
                if isinstance(field_value, str):
                    try:
                        if field_type_name == 'INTEGER':
                            field_value = int(field_value)
                        else:
                            field_value = float(field_value)
                    except (ValueError, TypeError):
                        # If conversion fails, don't accumulate
                        field_value = field.value
                
                # Accumulate the value
                if field_name in self.accumulated_results:
                    self.accumulated_results[field_name]['value'] += field_value
                else:
                    self.accumulated_results[field_name] = {
                        'value': field_value,
                        'type': field.field_type,
                        'description': field.description
                    }
            else:
                # For non-accumulated fields, just update the value
                self.accumulated_results[field_name] = {
                    'value': field_value,
                    'type': field.field_type,
                    'description': field.description
                }
        
        # Update the table
        self.update_results_table()

    def update_results_table(self):
        """Update the results table with the current accumulated results"""
        print(f"> Updating results table with {len(self.accumulated_results)} fields")
        
        # Clear the table
        self.results_table.setRowCount(0)
        
        # Add rows for each field
        for i, (name, data) in enumerate(self.accumulated_results.items()):
            self.results_table.insertRow(i)
            
            # Format the name with "Sum of" or "Last" prefix based on data type
            value = data['value']
            field_type = data.get('type')
            
            # Get the field type name as a string
            field_type_name = field_type.name if hasattr(field_type, 'name') else str(field_type)
            
            # Check if this field should be displayed as accumulated
            is_accumulated = False
            if isinstance(value, (int, float)) and field_type_name in ['INTEGER', 'FLOAT']:
                # Check if the field has been accumulated by looking at the original field
                is_accumulated = True
                
                # If it's a numeric type, format with comma for thousands
                value_str = f"{value:,}"
            elif isinstance(value, list):
                # Format lists with limited display
                value_str = ", ".join(str(item) for item in value[:3])
                if len(value) > 3:
                    value_str += f"... ({len(value)} items)"
            elif isinstance(value, dict):
                # Format dictionaries with summary
                value_str = f"{{...}} ({len(value)} key-value pairs)"
            else:
                # Format strings and other types
                value_str = str(value)
            
            # Add the prefix to the field name
            display_name = f"Sum of {name}" if is_accumulated else f"Last {name}"
            
            # Set the field name with appropriate prefix
            self.results_table.setItem(i, 0, QTableWidgetItem(display_name))
            
            # Set the value
            self.results_table.setItem(i, 1, QTableWidgetItem(value_str))
            
            # Add description if available
            if data.get('description'):
                self.results_table.setItem(i, 2, QTableWidgetItem(str(data['description'])))
            
            print(f">   Added row {i}: {display_name} = {value_str}")
        
        # Resize rows to contents
        self.results_table.resizeRowsToContents()
        
        # Resize the first column to contents to make room for the prefixes
        self.results_table.resizeColumnToContents(0)
        
        print(f"> Table updated with {self.results_table.rowCount()} rows")
        
        # Update the "done/total" counter
        self.update_done_total_counter()

    def update_done_total_counter(self):
        """Update the done/total counter"""
        done = self.success_count
        total = self.total_urls
        
        # Update the label with current progress
        if self.is_scraping:
            status = "Processing"
        else:
            status = "Completed"
        
        self.done_total_label.setText(f"{status}: {done}/{total}")

    def show_suspension_timer(self, seconds, reason):
        """Show a dialog with a countdown timer before resuming execution"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
        from PyQt5.QtCore import QTimer, Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Execution Suspended")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(200)
        
        layout = QVBoxLayout(dialog)
        
        # Message label
        message_label = QLabel(f"{reason}\n\nExecution will resume in {seconds} seconds...")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Timer countdown label
        timer_label = QLabel(f"{seconds}")
        timer_label.setAlignment(Qt.AlignCenter)
        font = timer_label.font()
        font.setPointSize(24)
        timer_label.setFont(font)
        layout.addWidget(timer_label)
        
        # Progress bar
        progress_bar = QProgressBar(dialog)
        progress_bar.setRange(0, seconds)
        progress_bar.setValue(seconds)
        layout.addWidget(progress_bar)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        
        # Resume button
        resume_button = QPushButton("Resume Now")
        
        # Add buttons to layout
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(resume_button)
        layout.addLayout(button_layout)
        
        # Create timer
        timer = QTimer(dialog)
        remaining = [seconds]  # Using list to store mutable value
        
        def update_timer():
            remaining[0] -= 1
            timer_label.setText(f"{remaining[0]}")
            progress_bar.setValue(remaining[0])
            message_label.setText(f"{reason}\n\nExecution will resume in {remaining[0]} seconds...")
            
            if remaining[0] <= 0:
                timer.stop()
                dialog.accept()
        
        # Connect buttons
        resume_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(lambda: self.cancel_scraping_from_dialog(dialog))
        
        # Connect and start the timer
        timer.timeout.connect(update_timer)
        timer.start(1000)  # Update every 1 second
        
        # Apply the same dark theme styling
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 2px solid #444444;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton {
                background-color: #FF6600;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF8533;
            }
            QPushButton[text="Cancel"] {
                background-color: #FF3333;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #FF5555;
            }
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 5px;
                text-align: center;
                background-color: #2D2D2D;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #FF6600;
            }
        """)
        
        # When dialog is closed (either by timer or button), check if we're cancelling or resuming
        if dialog.exec_() and self.worker and not self.worker.stop_execution:
            self.worker.is_suspended = False

    def cancel_scraping_from_dialog(self, dialog):
        """Cancel the scraping process from the suspension dialog"""
        # First cancel the scraping
        self.cancel_scraping()
        # Then close the dialog
        dialog.reject()
        
    def handle_url_status(self, status, url):
        """Handle URL status updates from the worker thread"""
        if status == 0:
            # Success
            self.success_count += 1
            self.add_url_to_in_tab(url, self.success_count)
        elif status == 1:
            # Warning (Cloudflare detected)
            self.warning_count += 1
            self.add_url_to_warning_tab(url, self.warning_count)
        elif status == 2:
            # Error
            self.error_count += 1
            self.add_url_to_error_tab(url, self.error_count)
        
        # Update the "done/total" counter
        self.update_done_total_counter()
    
    def remove_url_from_input(self, url):
        """Remove a successfully processed URL from the input text box"""
        # Get current URLs
        urls_text = self.file_path_input.toPlainText().strip()
        if not urls_text:
            return
            
        # Split into individual URLs
        urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
        
        # Remove the processed URL
        if url in urls:
            urls.remove(url)
            
        # Update the text box
        self.file_path_input.setText('\n'.join(urls))
    
    def scraping_finished(self):
        """Called when the scraping process finishes"""
        print(f"\n> Scraping process completed! Success: {self.success_count}, Warnings: {self.warning_count}, Errors: {self.error_count}")
        
        # Reset UI state
        self.is_scraping = False
        self.run_button.setEnabled(True)
        self.run_button.setText("RUN")
        self.cancel_button.setVisible(False)  # Hide cancel button
        self.cancel_button.setEnabled(True)   # Re-enable for next run
        
        # Re-enable the plugin dropdown
        self.plugin_dropdown.setEnabled(True)
        
        # Update the counter to show "Completed"
        self.update_done_total_counter()
        
        # Clean up the worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
    
    def cancel_scraping(self):
        """Cancel the scraping process"""
        if self.worker:
            # Set the stop flag
            self.worker.stop_execution = True
            # Also clear suspension if it's suspended
            self.worker.is_suspended = False
            
            # Update UI
            self.run_button.setText("CANCELLING...")
            self.cancel_button.setEnabled(False)

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScraperApp()
    sys.exit(app.exec_())