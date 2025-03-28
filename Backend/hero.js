// Import modules conditionally based on chosen engine
const heroModule = require('@ulixee/hero-playground');
const Hero = heroModule;
const fs = require('fs');
const path = require('path');
const { setTimeout } = require('timers/promises');

// Will be loaded on demand - with fallback mechanisms
let puppeteer;
let puppeteerExtra;
let stealthPlugin;


function validateUserAgent(userAgent) {
  // Basic validation - check if it contains only valid characters
  // This regex allows alphanumeric characters, common punctuation, and safe special characters
  const validPattern = /^[a-zA-Z0-9\s\.\,\/\-\_\:\;\(\)]+$/;
  return validPattern.test(userAgent);
}

// Read user agents from file
function loadUserAgents() {
  try {
    const filePath = path.join(process.cwd(), 'user-agents.txt');
    const fileContent = fs.readFileSync(filePath, 'utf8');
    // Split by newlines, filter out empty lines, trim whitespace, and validate
    const agents = fileContent.split('\n')
      .map(agent => agent.trim())
      .filter(agent => agent !== '')
      .map(agent => agent.replace(/\r/g, ''))
      .filter(agent => validateUserAgent(agent));
    
    if (agents.length === 0) {
      console.error('Warning: No valid user agents found. Using fallback user agents.');
      return [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
      ];
    }
    
    return agents;
  } catch (error) {
    console.error(`Error loading user agents from file: ${error.message}`);
    console.error('Using fallback user agents instead.');
    return [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    ];
  }
}

// Load user agents when the module is initialized
const userAgents = loadUserAgents();

// Realistic viewports
const viewports = [
  { width: 1920, height: 1080 },
  { width: 1680, height: 1050 },
  { width: 1440, height: 900 },
  { width: 1366, height: 768 },
  { width: 2560, height: 1440 }
];

// Random geolocation data (coordinates of major cities)
const geolocations = [
  { latitude: 40.7128, longitude: -74.0060 }, // New York
  { latitude: 34.0522, longitude: -118.2437 }, // Los Angeles
  { latitude: 51.5074, longitude: -0.1278 }, // London
  { latitude: 48.8566, longitude: 2.3522 }, // Paris
  { latitude: 35.6762, longitude: 139.6503 } // Tokyo
];

// Get random item from an array
function getRandomItem(array) {
  return array[Math.floor(Math.random() * array.length)];
}

// Wait for a random time between min and max milliseconds
async function randomDelay(min, max, fastMode = false) {
  if (fastMode) {
    // In fast mode, use significantly shorter delays
    min = Math.floor(min / 4);
    max = Math.floor(max / 4);
  }
  const delay = Math.floor(Math.random() * (max - min + 1) + min);
  await setTimeout(delay);
  return delay;
}

// Safely require a module, return null if it doesn't exist
function safeRequire(moduleName) {
  try {
    return require(moduleName);
  } catch (error) {
    if (error.code === 'MODULE_NOT_FOUND') {
      console.error(`Module '${moduleName}' not found. To use this feature, install it with: npm install ${moduleName}`);
      return null;
    }
    throw error;
  }
}

async function getHtml(url, options = {}) {
  const defaultOptions = {
    engine: 'hero', // 'hero', 'puppeteer', 'puppeteer-extra', 'puppeteer-stealth'
    headless: true,
    timeout: 60000, // Increased timeout for Cloudflare challenges
    blockedResourceTypes: ['BlockImages', 'BlockFonts'], // Block non-essential resources
    userAgent: '~ chrome >= 105 && windows >= 10',
    viewport: getRandomItem(viewports),
    geolocation: getRandomItem(geolocations),
    extraHeaders: {},
    cookies: [],
    waitForSelector: '', // Optional selector to wait for before returning HTML
    bypassCloudflare: true, // Enable specific Cloudflare bypass techniques
    humanBehavior: true, // Enable human-like behavior simulation
    debugScreenshots: false, // Take debug screenshots
    screenshotPath: path.join(process.cwd(), 'screenshots'),
    fastMode: false, // New parameter for speed optimization
    waitUntil: 'networkidle2' // Default event to wait for - will change to 'domcontentloaded' in fast mode
  };
  
  const config = { ...defaultOptions, ...options };
  
  console.error(`Fetching HTML from: ${url}`);
  console.error(`Engine: ${config.engine}, Headless: ${config.headless}`);
  
  // Override waitUntil in fast mode for puppeteer engines
  if (config.fastMode && (config.engine.includes('puppeteer'))) {
    config.waitUntil = 'domcontentloaded'; // Much faster than networkidle2
    // Add more aggressive resource blocking in fast mode
    if (!config.blockedResourceTypes.includes('BlockMedia')) {
      config.blockedResourceTypes.push('BlockMedia');
    }
  }

  // Reduce logging in fast mode
  if (!config.fastMode || config.debugScreenshots) {
    console.error(`Fetching HTML from: ${url}`);
    console.error(`Engine: ${config.engine}, Headless: ${config.headless}, Fast Mode: ${config.fastMode}`);
  }

  // Create screenshots directory if debug screenshots enabled
  if (config.debugScreenshots) {
    try {
      if (!fs.existsSync(config.screenshotPath)) {
        fs.mkdirSync(config.screenshotPath, { recursive: true });
      }
    } catch (err) {
      console.error(`Failed to create screenshots directory: ${err.message}`);
    }
  }
  
  // Choose appropriate engine
  switch (config.engine) {
    case 'hero':
      return fetchWithHero(url, config);
    case 'puppeteer':
      return fetchWithPuppeteer(url, config);
    case 'puppeteer-extra':
      return fetchWithPuppeteerExtra(url, config, false);
    case 'puppeteer-stealth':
      return fetchWithPuppeteerExtra(url, config, true);
    default:
      throw new Error(`Unknown engine: ${config.engine}`);
  }
}

async function simulateHumanBehavior(page, config, engine = 'hero') {
  // Skip completely if in fast mode and human behavior not explicitly requested
  if (config.fastMode && !config.humanBehavior) return;
  
  if (!config.fastMode) console.error('Simulating human behavior...');
  
  try {
    // Use shorter delay in fast mode
    await randomDelay(1000, 3000, config.fastMode);
    
    // Reduce number of scroll steps in fast mode
    const scrollSteps = config.fastMode ? 1 : (Math.floor(Math.random() * 5) + 2);
    
    for (let i = 0; i < scrollSteps; i++) {
      // Smaller scroll amounts in fast mode
      const scrollAmount = Math.floor((Math.random() * (config.fastMode ? 300 : 500)) + 
                                     (config.fastMode ? 100 : 200));
      
      if (engine === 'hero') {
        // Hero scrolling
        await page.scrollTo([0, scrollAmount * (i + 1)]);
        
        // Skip mouse movements in fast mode
        if (!config.fastMode) {
          const x = Math.floor(Math.random() * config.viewport.width * 0.8) + 50;
          const y = Math.floor(Math.random() * scrollAmount * (i + 0.5) + 100);
          await page.interact({ move: [x, y] });
        }
      } else {
        // Puppeteer scrolling
        await page.evaluate((scrollY) => {
          window.scrollBy(0, scrollY);
        }, scrollAmount);
        
        // Skip mouse movements in fast mode
        if (!config.fastMode) {
          const x = Math.floor(Math.random() * config.viewport.width * 0.8) + 50;
          const y = Math.floor(Math.random() * scrollAmount * (i + 0.5) + 100);
          await page.mouse.move(x, y);
        }
      }
      
      // Faster delays between scrolls in fast mode
      await randomDelay(500, 2000, config.fastMode);
    }
    
    // Rest of function remains the same...
  } catch (error) {
    // Error handling remains the same...
  }
}

async function handleCloudflareChallenge(page, config, engine = 'hero') {
  if (!config.fastMode) console.error('Handling potential Cloudflare challenge...');
  
  try {
    // Take debug screenshot if enabled
    if (config.debugScreenshots) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const screenshotPath = path.join(config.screenshotPath, `cloudflare-initial-${timestamp}.png`);
      
      if (engine === 'hero') {
        await page.takeScreenshot({ path: screenshotPath });
      } else {
        await page.screenshot({ path: screenshotPath });
      }
      console.error(`Saved Cloudflare initial screenshot to: ${screenshotPath}`);
    }
    
    // Check for Cloudflare challenge page
    const cloudflareDetected = await (engine === 'hero' 
      ? page.document.querySelector('#cf-wrapper').$exists
      : page.evaluate(() => {
          return !!document.querySelector('#cf-wrapper') || 
                 document.title.includes('Cloudflare') ||
                 document.title.includes('Security Check') ||
                 document.body.textContent.includes('Checking your browser');
        })
    );
    
    if (cloudflareDetected) {
      console.error('Cloudflare challenge detected, waiting for resolution...');
      
      // Wait longer for Cloudflare challenge to resolve
      const challengeTimeout = config.fastMode ? config.timeout : config.timeout * 1.5;
      const checkInterval = config.fastMode ? 1000 : 2000;
      const maxChecks = Math.floor(challengeTimeout / checkInterval);
      
      for (let i = 0; i < maxChecks; i++) {
        // Wait between checks
        await randomDelay(checkInterval, checkInterval + (config.fastMode ? 500 : 1000), config.fastMode);
        
        // Check if challenge is still present
        const stillOnChallenge = await (engine === 'hero'
          ? page.document.querySelector('#cf-wrapper').$exists
          : page.evaluate(() => {
              return !!document.querySelector('#cf-wrapper') || 
                     document.title.includes('Cloudflare') ||
                     document.title.includes('Security Check');
            })
        );
        
        if (!stillOnChallenge) {
          console.error(`Cloudflare challenge passed after ${i+1} checks`);
          
          // Take debug screenshot if enabled
          if (config.debugScreenshots) {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const screenshotPath = path.join(config.screenshotPath, `cloudflare-passed-${timestamp}.png`);
            
            if (engine === 'hero') {
              await page.takeScreenshot({ path: screenshotPath });
            } else {
              await page.screenshot({ path: screenshotPath });
            }
            console.error(`Saved Cloudflare resolved screenshot to: ${screenshotPath}`);
          }
          
          // Additional wait for page to stabilize after challenge
          await randomDelay(2000, 4000);
          return true;
        }
      }
      
      console.error('Failed to bypass Cloudflare challenge within timeout');
      return false;
    } else {
      if (!config.fastMode) console.error('No Cloudflare challenge detected');
      return true;
    }
  } catch (error) {
    console.error(`Error while handling Cloudflare challenge: ${error.message}`);
    return false;
  }
}

async function fetchWithHero(url, config) {
  let hero = null;
  
  try {
    if (!config.fastMode) console.error('Initializing Hero with enhanced settings...');
    
    // Create a new Hero instance with advanced settings
    hero = new Hero({
      showChrome: config.headless === false, // Show browser window when headless is false
      blockedResourceTypes: config.blockedResourceTypes,
      viewport: config.viewport,
      userAgent: `~ ${/chrome/i.test(config.userAgent) ? 'chrome' : 'safari'} >= 110`,
      geolocation: config.geolocation,
      upstreamProxyUrl: config.proxyUrl || null,
      showChromeInteractions: !config.headless, // Show interactions in visible mode
      timezoneId: config.timezoneId || null,
      locale: config.locale || 'en-US'
    });
    
    // Set cookies if provided
    if (config.cookies && config.cookies.length > 0) {
      await hero.goto('about:blank');
      for (const cookie of config.cookies) {
        await hero.activeTab.cookieStorage.setItem(
          cookie.name,
          cookie.value,
          cookie.expires,
          {
            domain: cookie.domain,
            path: cookie.path || '/',
            httpOnly: cookie.httpOnly || false,
            secure: cookie.secure || false,
            sameSite: cookie.sameSite || 'Lax'
          }
        );
      }
    }
    
    console.error(`Navigating to: ${url}`);
    
    // Navigate to the URL with extended timeout
    await hero.goto(url, { 
      timeoutMs: config.timeout,
      referrer: config.referrer || null
    });
    
    // Handle Cloudflare if needed
    if (config.bypassCloudflare) {
      const passedCloudflare = await handleCloudflareChallenge(hero, config, 'hero');
      if (!passedCloudflare) {
        console.error('Could not verify Cloudflare bypass. Continuing anyway...');
      }
    }
    
    // Simulate human behavior if enabled
    if (config.humanBehavior) {
      await simulateHumanBehavior(hero, config, 'hero');
    }
    
    // Wait for specific selector if provided
    if (config.waitForSelector) {
      try {
        const element = hero.document.querySelector(config.waitForSelector);
        await element.$waitForVisible({ timeoutMs: config.fastMode ? 5000 : 10000 });
        if (!config.fastMode) console.error(`Found selector: ${config.waitForSelector}`);
      } catch (selectorError) {
        if (!config.fastMode) console.error(`Could not find selector "${config.waitForSelector}": ${selectorError.message}`);
      }
    }
    
    // Wait for any remaining network activity to settle
    await randomDelay(1000, 3000, config.fastMode);
    
    // Get the HTML content
    const html = await hero.document.documentElement.outerHTML;
    
    console.error(`Successfully fetched HTML with Hero (${html.length} characters)`);
    return html;
    
  } catch (error) {
    console.error(`Error fetching HTML with Hero: ${error.message}`);
    
    // Take error screenshot if debug enabled
    if (config.debugScreenshots && hero) {
      try {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const screenshotPath = path.join(config.screenshotPath, `error-hero-${timestamp}.png`);
        await hero.takeScreenshot({ path: screenshotPath });
        console.error(`Saved error screenshot to: ${screenshotPath}`);
      } catch (screenshotError) {
        console.error(`Failed to take error screenshot: ${screenshotError.message}`);
      }
    }
    
    throw error;
  } finally {
    // Clean up
    if (hero) {
      try {
        await hero.close();
        console.error('Hero browser closed');
      } catch (closeError) {
        console.error(`Error closing Hero browser: ${closeError.message}`);
      }
    }
  }
}

async function configurePuppeteerForCloudflare(browser, page, config) {
  // Set viewport
  await page.setViewport(config.viewport);
  
  // Set user agent
  await page.setUserAgent(config.userAgent);
  
  // Set extra headers if provided
  if (config.extraHeaders && Object.keys(config.extraHeaders).length > 0) {
    await page.setExtraHTTPHeaders(config.extraHeaders);
  }
  
  // Set cookies if provided
  if (config.cookies && config.cookies.length > 0) {
    await page.setCookie(...config.cookies);
  }
  
  // Inject navigator.webdriver fix
  await page.evaluateOnNewDocument(() => {
    // Overwrite the webdriver property
    Object.defineProperty(navigator, 'webdriver', {
      get: () => false,
    });
    
    // Create a fake permissions API to fool fingerprinting
    if (!('permissions' in navigator)) {
      navigator.permissions = {
        query: () => Promise.resolve({ state: 'granted' }),
      };
    }
    
    // Add plugins array
    if (navigator.plugins.length === 0) {
      Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5].map(() => ({
          name: 'Chrome PDF Plugin',
          description: 'Portable Document Format',
          filename: 'internal-pdf-viewer',
          length: 1,
        })),
      });
    }
    
    // WebGL fingerprinting
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
      // UNMASKED_VENDOR_WEBGL
      if (parameter === 37445) {
        return 'Intel Inc.';
      }
      // UNMASKED_RENDERER_WEBGL
      if (parameter === 37446) {
        return 'Intel Iris OpenGL Engine';
      }
      return getParameter.call(this, parameter);
    };
    
    // Add language and platform consistency
    const getOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
    Object.getOwnPropertyDescriptor = function(obj, prop) {
      if (prop === 'languages' || prop === 'platform') {
        return undefined;
      }
      return getOwnPropertyDescriptor(obj, prop);
    };
  });
  
  return page;
}

async function fetchWithPuppeteer(url, config) {
  // Lazy load puppeteer
  puppeteer = safeRequire('puppeteer');
  if (!puppeteer) {
    throw new Error('Puppeteer is required but not installed. Please run: npm install puppeteer');
  }
  
  let browser = null;
  
  try {
    console.error('Launching standard Puppeteer with enhanced settings...');
    
    // Launch browser with additional arguments to avoid detection
    browser = await puppeteer.launch({
      headless: config.headless === false ? false : "new",
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-infobars',
        '--window-position=0,0',
        '--ignore-certifcate-errors',
        '--ignore-certifcate-errors-spki-list',
        '--disable-features=IsolateOrigins,site-per-process',
        `--window-size=${config.viewport.width},${config.viewport.height}`,
        '--disable-extensions',
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security'
      ],
      defaultViewport: null, // Use window size for viewport
      ignoreHTTPSErrors: true
    });
    
    // Open a new page
    const page = await browser.newPage();
    
    // Configure for Cloudflare bypass
    await configurePuppeteerForCloudflare(browser, page, config);
    
    // Set timeout
    page.setDefaultNavigationTimeout(config.timeout);
    
    console.error(`Navigating to: ${url}`);
    
    // Navigate to the URL with wait options
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: config.timeout
    });
    
    // Handle Cloudflare if needed
    if (config.bypassCloudflare) {
      const passedCloudflare = await handleCloudflareChallenge(page, config, 'puppeteer');
      if (!passedCloudflare) {
        console.error('Could not verify Cloudflare bypass. Continuing anyway...');
      }
    }
    
    // Simulate human behavior if enabled
    if (config.humanBehavior) {
      await simulateHumanBehavior(page, config, 'puppeteer');
    }
    
    // Wait for specific selector if provided
    if (config.waitForSelector) {
      try {
        await page.waitForSelector(config.waitForSelector, { 
          visible: true, 
          timeout: 10000 
        });
        console.error(`Found selector: ${config.waitForSelector}`);
      } catch (selectorError) {
        console.error(`Could not find selector "${config.waitForSelector}": ${selectorError.message}`);
      }
    }
    
    // Wait for any remaining network activity to settle
    await randomDelay(1000, 3000);
    
    // Get the HTML content
    const html = await page.content();
    
    console.error(`Successfully fetched HTML with Puppeteer (${html.length} characters)`);
    return html;
    
  } catch (error) {
    console.error(`Error fetching HTML with Puppeteer: ${error.message}`);
    
    // Take error screenshot if debug enabled
    if (config.debugScreenshots && browser) {
      try {
        const pages = await browser.pages();
        const activePage = pages[0];
        if (activePage) {
          const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
          const screenshotPath = path.join(config.screenshotPath, `error-puppeteer-${timestamp}.png`);
          await activePage.screenshot({ path: screenshotPath });
          console.error(`Saved error screenshot to: ${screenshotPath}`);
        }
      } catch (screenshotError) {
        console.error(`Failed to take error screenshot: ${screenshotError.message}`);
      }
    }
    
    throw error;
  } finally {
    // Clean up
    if (browser) {
      try {
        await browser.close();
        console.error('Puppeteer browser closed');
      } catch (closeError) {
        console.error(`Error closing Puppeteer browser: ${closeError.message}`);
      }
    }
  }
}

async function fetchWithPuppeteerExtra(url, config, useStealthPlugin) {
  // Lazy load puppeteer-extra and plugins
  puppeteerExtra = safeRequire('puppeteer-extra');
  if (!puppeteerExtra) {
    throw new Error('puppeteer-extra is required but not installed. Please run: npm install puppeteer puppeteer-extra');
  }
  
  // Load puppeteer if not already loaded
  puppeteer = puppeteer || safeRequire('puppeteer');
  if (!puppeteer) {
    throw new Error('puppeteer is required but not installed. Please run: npm install puppeteer');
  }
  
  // Add stealth plugin if requested
  if (useStealthPlugin) {
    stealthPlugin = stealthPlugin || safeRequire('puppeteer-extra-plugin-stealth');
    if (stealthPlugin) {
      puppeteerExtra.use(stealthPlugin());
      console.error('Using stealth plugin');
    } else {
      console.error('Stealth plugin requested but not installed. Continuing without it.');
      console.error('To install, run: npm install puppeteer-extra-plugin-stealth');
    }
  }
  
  // We'll skip loading the other plugins if they're not available
  // and continue with basic anti-detection measures
  
  let browser = null;
  
  try {
    console.error(`Launching Puppeteer-Extra${useStealthPlugin ? ' with Stealth' : ''} with enhanced settings...`);
    
    // Launch browser with additional arguments to avoid detection
    browser = await puppeteerExtra.launch({
      headless: config.headless === false ? false : "new",
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-infobars',
        '--window-position=0,0',
        '--ignore-certifcate-errors',
        '--ignore-certifcate-errors-spki-list',
        '--disable-features=IsolateOrigins,site-per-process',
        `--window-size=${config.viewport.width},${config.viewport.height}`,
        '--disable-extensions',
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security'
      ],
      defaultViewport: null, // Use window size for viewport
      ignoreHTTPSErrors: true
    });
    
    // Open a new page
    const page = await browser.newPage();
    
    // Configure for Cloudflare bypass
    await configurePuppeteerForCloudflare(browser, page, config);
    
    // Set timeout
    page.setDefaultNavigationTimeout(config.timeout);
    
    console.error(`Navigating to: ${url}`);
    
    // Navigate to the URL with wait options
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: config.timeout
    });
    
    // Handle Cloudflare if needed
    if (config.bypassCloudflare) {
      const passedCloudflare = await handleCloudflareChallenge(page, config, 'puppeteer');
      if (!passedCloudflare) {
        console.error('Could not verify Cloudflare bypass. Continuing anyway...');
      }
    }
    
    // Simulate human behavior if enabled
    if (config.humanBehavior) {
      await simulateHumanBehavior(page, config, 'puppeteer');
    }
    
    // Wait for specific selector if provided
    if (config.waitForSelector) {
      try {
        await page.waitForSelector(config.waitForSelector, { 
          visible: true, 
          timeout: 10000 
        });
        console.error(`Found selector: ${config.waitForSelector}`);
      } catch (selectorError) {
        console.error(`Could not find selector "${config.waitForSelector}": ${selectorError.message}`);
      }
    }
    
    // Wait for any remaining network activity to settle
    await randomDelay(1000, 3000);
    
    // Get the HTML content
    const html = await page.content();
    
    console.error(`Successfully fetched HTML with Puppeteer${useStealthPlugin ? ' + Stealth' : ' Extra'} (${html.length} characters)`);
    return html;
    
  } catch (error) {
    console.error(`Error fetching HTML with Puppeteer${useStealthPlugin ? ' + Stealth' : ' Extra'}: ${error.message}`);
    
    // Take error screenshot if debug enabled
    if (config.debugScreenshots && browser) {
      try {
        const pages = await browser.pages();
        const activePage = pages[0];
        if (activePage) {
          const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
          const screenshotPath = path.join(config.screenshotPath, `error-puppeteer-extra-${timestamp}.png`);
          await activePage.screenshot({ path: screenshotPath });
          console.error(`Saved error screenshot to: ${screenshotPath}`);
        }
      } catch (screenshotError) {
        console.error(`Failed to take error screenshot: ${screenshotError.message}`);
      }
    }
    
    throw error;
  } finally {
    // Clean up
    if (browser) {
      try {
        await browser.close();
        console.error('Puppeteer browser closed');
      } catch (closeError) {
        console.error(`Error closing Puppeteer browser: ${closeError.message}`);
      }
    }
  }
}

// Process command line arguments
async function main() {
  // Check if config file is provided
  const configIndex = process.argv.indexOf('--config');
  if (configIndex !== -1 && configIndex + 1 < process.argv.length) {
    // Get the configuration file path
    const configFilePath = process.argv[configIndex + 1];
    
    try {
      // Read and parse the config file
      const configData = fs.readFileSync(configFilePath, 'utf8');
      const config = JSON.parse(configData);
      
      try {
        // Use console.error for logs to keep stdout clean for the HTML output
        const originalConsoleLog = console.log;
        console.log = console.error;
        
        // Fetch the HTML with the provided configuration
        const html = await getHtml(config.url, config);
        
        // Restore console.log for the HTML output
        console.log = originalConsoleLog;
        
        // Output ONLY the HTML to stdout (no logs)
        console.log(html);
        
      } catch (error) {
        console.error('Failed to fetch HTML:');
        console.error(error);
        process.exit(1);
      }
    } catch (error) {
      console.error(`Error reading or parsing config file: ${error.message}`);
      process.exit(1);
    }
  } else {
    // Legacy command line argument processing
    const url = process.argv[2];
    
    if (!url) {
      console.error('Please provide a URL as an argument');
      console.error('Usage: node hero.js <url> [engine] [headless]');
      console.error('Or: node hero.js --config <config.json>');
      process.exit(1);
    }
    
    // Get engine option
    const engine = process.argv[3] || 'hero';
    
    // Check if headless mode is specified
    const headless = process.argv[4] !== 'visible';

    // Check for fast mode
    const fastMode = process.argv[5] === 'fast';
    
    try {
      // Redirect logs to stderr
      const originalConsoleLog = console.log;
      console.log = console.error;
      
      const html = await getHtml(url, { 
        engine,
        headless,
        bypassCloudflare: true,
        humanBehavior: !fastMode, // Disable human behavior in fast mode
        debugScreenshots: false,
        fastMode
      });
      
      // Restore console.log for the HTML output
      console.log = originalConsoleLog;
      
      // Output ONLY the HTML to stdout
      console.log(html);
      
    } catch (error) {
      console.error('Failed to fetch HTML:');
      console.error(error);
      process.exit(1);
    }
  }
}

// Export the getHtml function for use in other files
module.exports = {
  getHtml
};

// Run the script if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Unhandled error:');
    console.error(error);
    process.exit(1);
  });
}