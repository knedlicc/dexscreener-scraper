# 🔍 DexScreener Contract Scraper

A robust web scraping tool designed to extract token contract addresses of new pairs from [DexScreener.com](https://dexscreener.com). This utility leverages undetected ChromeDriver to bypass anti-bot protections and intelligently handles Cloudflare challenges.

## ✨ Features

- 🛡️ **Anti-Detection Measures**: Uses undetected_chromedriver to bypass common bot detection mechanisms
- ☁️ **Cloudflare Handling**: Automatically handles Cloudflare protection with manual fallback if needed
- ⛓️ **Multi-Chain Support**: Works with Ethereum, BSC, Polygon, Avalanche, and other networks
- 🔧 **Flexible Filtering**: Filter tokens by trending score, volume, liquidity, and age
- 🔄 **Custom Sorting**: Arrange results in ascending or descending order
- 📄 **Simple Output**: Saves clean contract addresses to a text file

## 🚀 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/knedlicc/dexscreener-scraper.git
   cd dexscreener-scraper
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have latest Chrome browser installed on your system.

## 📋 Usage

### Command Line Execution

Simply run the script:
```bash
python scraper.py
```
### Custom Configuration

Edit the `main()` function in the script to customize parameters:
```python
def main():
    scrape_dexscreener(
        chain="ethereum",          # Choose blockchain network
        rank_by="trendingScoreH6", # Sort by trending score
        order="desc",              # Descending order
        min_liquidity=25000,       # Minimum $25,000 liquidity
        max_age=720,               # Tokens less than 12 hours old
        output_file="eth_contracts.txt" # Output filename
    )
```

### Configuration Parameters

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `chain` | Blockchain to scrape | `"ethereum"` | `"ethereum"`, `"bsc"`, `"polygon"`, `"avalanche"`, etc. |
| `rank_by` | Ranking metric | `"trendingScoreH6"` | `"trendingScoreH6"`, `"volume"`, `"marketCap"`, etc. |
| `order` | Sort order | `"desc"` | `"asc"`, `"desc"` |
| `min_liquidity` | Minimum liquidity in USD | `25000` | Any positive integer |
| `max_age` | Max pair age in minutes | `720` | Any positive integer |
| `output_file` | Output file name | `"{chain}_contracts.txt"` | Any valid filename |

## 🛡️ Handling Cloudflare Protection

The script is designed to wait for automatic Cloudflare resolution. If automatic resolution fails, it will prompt you to:

1. Manually solve any CAPTCHA in the browser window
2. Press Enter once complete

## ⚙️ How It Works

1. 🌐 The script initializes an undetected Chrome browser
2. 🔍 Navigates to DexScreener's new pairs page with your specified filters
3. ⏳ Waits for the page to load and handles any Cloudflare challenges
4. 📥 Extracts contract addresses from the page
5. 💾 Saves the addresses to a text file
6. 🧹 Properly cleans up by closing the browser

## 🔧 Troubleshooting

- 🌐 **Browser Not Starting**: Ensure Chrome is installed and up-to-date
- 📭 **No Addresses Found**: Check your filter parameters or network connectivity
- 🛡️ **Cloudflare Issues**: The script may need manual intervention for CAPTCHA solving
- ⏱️ **Script Hanging**: Check your internet connection or try increasing timeout values

## 📦 Requirements

- Python 3.7+
- Chrome web browser
- Dependencies:
  - undetected_chromedriver>=3.5.0
  - selenium>=4.10.0
  - beautifulsoup4>=4.12.0

## 📜 License

MIT License
