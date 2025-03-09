import os
import random
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Patch the Chrome.__del__ method to avoid OSError
def patched_del(self):
    try:
        self.quit()
    except OSError:  # Suppress [WinError 6]
        pass
    except Exception as e:  # Catch non-critical errors
        print(f"⚠️  Non-critical error during Chrome destructor: {e}")

uc.Chrome.__del__ = patched_del  # Apply the patch

# Clear any existing proxy settings
if 'http_proxy' in os.environ:
    del os.environ['http_proxy']
if 'https_proxy' in os.environ:
    del os.environ['https_proxy']

def create_driver():
    """Create and configure the undetected ChromeDriver."""
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    try:
        driver = uc.Chrome(options=options)
        print("✅ Browser initialized successfully.")
        return driver
    except Exception as e:
        print(f"❌ Error creating browser: {str(e)}")
        raise

def wait_for_page_load(driver, timeout=10):
    """Wait for the page to fully load."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except Exception as e:
        print(f"⚠️  Page load timeout: {str(e)}")

def is_cloudflare_active(driver):
    """Check if Cloudflare challenge is currently active."""
    page_source = driver.page_source.lower()
    cloudflare_indicators = [ 
        'cloudflare',
        'checking your browser',
        'security check',
        'cf-challenge',
        'hcaptcha',
        'turnstile',
    ]
    return any(indicator in page_source for indicator in cloudflare_indicators)

def is_content_loaded(driver, timeout=10):
    """
    Reliable detection of DexScreener content loading.
    Uses a dual approach: confirming we're NOT on Cloudflare AND confirming we ARE on DexScreener.
    """
    # Try to locate actual data elements with short timeout
    try:
        # Check for DexScreener-specific tables or data containers
        wait = WebDriverWait(driver, timeout)
        
        # Method 1: Check for token prices (most reliable indicator)
        price_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'price') or contains(text(), '$')]")
        
        # Method 2: Check for token pair links
        token_pairs = driver.find_elements(By.XPATH, "//a[contains(@href, '/0x')]")
        
        # Method 3: Try to find the data grid/table with token information
        data_grid = len(driver.find_elements(By.XPATH, "//div[contains(@class, 'table') or contains(@class, 'grid')]")) > 0
        
        # Method 4: Look for specific DexScreener UI components
        dex_ui = len(driver.find_elements(By.XPATH, "//div[contains(@class, 'dexscreener') or contains(@class, 'tokendata')]")) > 0
        
        content_loaded = (len(price_elements) > 0 or len(token_pairs) > 3 or data_grid or dex_ui)
        
        # Additional verification: check URL structure
        valid_url = any(segment in driver.current_url.lower() for segment in 
                        ['dexscreener.com/ethereum', 
                         'dexscreener.com/bsc',
                         'dexscreener.com/polygon',
                         'dexscreener.com/avalanche',
                         'dexscreener.com/new-pairs'])
            
        return content_loaded and valid_url
        
    except Exception as e:
        print(f"⚠️ Error checking for DexScreener content: {e}")
        return False
    
def wait_for_cloudflare(driver, min_wait=5, max_wait=10):
    """Handle Cloudflare verification with automatic and manual fallback."""
    print("⚠️  Cloudflare verification detected.")
    print(f"⏳ Waiting {min_wait}-{max_wait} seconds for automatic resolution... don't do anything")
    time.sleep(random.uniform(min_wait, max_wait))
    if is_content_loaded(driver):
        print("✅ Cloudflare resolved automatically.")
        return
    print("⚠️  Manual verification required. Complete the CAPTCHA and press Enter.")
    input("Press Enter after solving the CAPTCHA...")

def parse_contracts(page_source, chain="ethereum"):
    """Extract contract addresses from page source."""
    soup = BeautifulSoup(page_source, "html.parser")
    contracts = set()
    for link in soup.find_all("a", href=True):
        if f"/{chain}/" in link["href"]:
            contract = link["href"].split("/")[-1]
            contracts.add(contract)
    return contracts

def scrape_dexscreener(
    chain="ethereum", 
    rank_by="trendingScoreH6", 
    order="desc", 
    min_liquidity=25000, 
    max_age=720, 
    output_file=None
):
    """
    Main function to scrape DexScreener tokens.
    Parameters:
    - chain (str): Blockchain (e.g., "ethereum", "bsc")
    - rank_by (str): How to rank results (e.g., "trendingScoreH6", "volume", "marketCap")
    - order (str): Order of results (e.g., "asc", "desc")
    - min_liquidity (int): Minimum liquidity (e.g., 25000)
    - max_age (int): Maximum age of pairs in minutes (e.g., 720)
    - output_file (str): Name of the file to save results
    """
    if output_file is None:
        output_file = f"{chain}_contracts.txt"
    
    driver = None
    contracts = []
    
    # Dynamically construct the URL with the passed filters
    base_url = f"https://dexscreener.com/new-pairs/{chain}"
    filters = f"?rankBy={rank_by}&order={order}&minLiq={min_liquidity}&maxAge={max_age}"
    url = base_url + filters
    try:
        print(f"🚀 Launching browser and accessing {url}...")
        driver = create_driver()
        driver.get(url)
        wait_for_page_load(driver)
        # Check for Cloudflare protection
        if is_cloudflare_active(driver):
            wait_for_cloudflare(driver)
        # Parse contract addresses
        contracts_on_page = parse_contracts(driver.page_source, chain)
        contracts.extend(contracts_on_page)
        print(f"✅ Found {len(contracts_on_page)} contracts from the page.")
        # Save contracts to a file
        with open(output_file, "w") as f:
            for contract in contracts:
                f.write(contract + "\n")
        print(f"💾 Saved {len(contracts)} contracts to {output_file}.")
    
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
    
    finally:
        # Ensure the browser is closed properly
        if driver:
            print("🛑 Closing browser...")
            try:
                driver.quit()
            except Exception as e:
                print(f"⚠️ Error during browser shutdown: {e}")

def main():
    # Example usage with user-defined filters
    scrape_dexscreener(
        chain="ethereum",  # Ethereum chain
        rank_by="trendingScoreH6",  # Rank by trending score (6h)
        order="asc",  # Ascending order
        min_liquidity=25000,  # Minimum liquidity
        max_age=720,  # 12 hours (720 minutes)
        output_file="eth_contracts.txt"  # Output file
    )

if __name__ == "__main__":
    main()
