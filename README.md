# Zillow Property Data Scraper

A Python command-line tool for scraping property data from Zillow listing URLs for personal educational use.

## ⚠️ Legal Disclaimer

**This tool is for personal, educational use only.** Web scraping may be subject to terms of service restrictions. Users are responsible for ensuring their use complies with:
- Zillow's Terms of Use
- Applicable laws and regulations
- Ethical web scraping practices

This tool implements respectful scraping practices including rate limiting and realistic delays.

## Features

- Extract key property data: Address, Lot Size, Price, Price/sqft, Days on Market
- Single URL or batch processing from file
- Automatic rate limiting (5-8 second delays between requests)
- Comprehensive error handling and logging
- Progress tracking with console output
- Timestamped CSV output
- URL validation for Zillow domains
- Volume warnings for large batches (>20 URLs)

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository:
```bash
git clone <repository-url>
cd DD-webscraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests beautifulsoup4 lxml
```

## Usage

### Basic Commands

**Scrape a single URL:**
```bash
python scraper.py "https://www.zillow.com/homedetails/123-Main-St-City-State-12345/123456789_zpid/"
```

**Scrape multiple URLs from a file:**
```bash
python scraper.py --file urls.txt
```

**Specify custom output filename:**
```bash
python scraper.py --file urls.txt --output my_results.csv
```

**Append to existing CSV file:**
```bash
python scraper.py --file urls.txt --append
```

### Command-Line Options

```
usage: scraper.py [-h] (url | --file FILE) [--output OUTPUT] [--append]

Zillow Property Data Scraper - For personal educational use only

positional arguments:
  url                   Single Zillow listing URL to scrape

optional arguments:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  Path to text file containing URLs (one per line)
  --output OUTPUT, -o OUTPUT
                        Output CSV filename (default: timestamped)
  --append, -a          Append to existing output file instead of creating new
```

## Input File Format

Create a text file with one Zillow URL per line:

```
# urls.txt
https://www.zillow.com/homedetails/123-Main-St/123456789_zpid/
https://www.zillow.com/homedetails/456-Oak-Ave/987654321_zpid/
https://www.zillow.com/homedetails/789-Pine-Rd/555555555_zpid/
```

Lines starting with `#` are treated as comments and ignored.

## Output Format

Results are saved to a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `url` | Original Zillow listing URL |
| `address` | Full property address |
| `lot_size` | Lot size (with units: sqft or acres) |
| `price` | Listing price |
| `price_per_sqft` | Price per square foot |
| `days_on_market` | Days on Zillow/market |
| `scrape_timestamp` | When the data was scraped |
| `error` | Error message if scraping failed, otherwise empty |

### Example Output

```csv
url,address,lot_size,price,price_per_sqft,days_on_market,scrape_timestamp,error
https://www.zillow.com/homedetails/123-Main-St/123456789_zpid/,123 Main St City ST 12345,0.25 acres,$450000,$250,45 days,2025-11-08 14:30:15,
```

If a field cannot be extracted, it will show `N/A`.

## Example Test URLs

Here are some example Zillow URLs for testing (Note: These may become outdated):

```
https://www.zillow.com/homedetails/2114-Bigelow-Ave-N-Seattle-WA-98109/48749107_zpid/
https://www.zillow.com/homedetails/308-N-Adelaide-Ave-Normal-IL-61761/5444155_zpid/
https://www.zillow.com/homedetails/1234-Main-St-Austin-TX-78701/29383848_zpid/
```

**Note:** Zillow's page structure may change over time. If scraping fails, the page structure may have been updated.

## Rate Limiting & Best Practices

This scraper implements several best practices:

- **Random delays:** 5-8 seconds between requests to avoid overwhelming servers
- **Single-threaded:** No parallel requests
- **Timeout protection:** 30-second timeout per request
- **Volume limit:** Warning for batches >20 URLs
- **No retries:** Failed requests are logged but not automatically retried
- **Realistic headers:** Uses browser-like User-Agent string

### Estimated Time

For a batch of URLs, expect approximately:
- 20 URLs: ~2-3 minutes
- 50 URLs: ~5-7 minutes
- 100 URLs: ~10-14 minutes

## Error Handling

The scraper handles various error conditions gracefully:

- **Invalid URLs:** Validates Zillow domain before scraping
- **Network errors:** Catches timeouts and connection failures
- **HTTP errors:** Handles 404, 403, 500 errors
- **Missing data:** Returns "N/A" for fields that can't be found
- **Parsing errors:** Logs errors and continues with remaining URLs

All errors are:
1. Displayed in console during execution
2. Saved in the `error` column of the CSV
3. Logged to `scraper_errors.log` file

## Troubleshooting

### Common Issues

**"Invalid Zillow URL" error:**
- Ensure URLs contain `zillow.com` in the domain
- Check that URLs are complete (include `https://`)

**"Request timeout" error:**
- Your internet connection may be slow
- Zillow's servers may be temporarily unavailable
- Try again later

**All fields show "N/A":**
- Zillow may have changed their page structure
- The listing may be in an unsupported format
- Check the error log for details

**HTTP 403 Forbidden:**
- You may have made too many requests too quickly
- Wait several minutes before trying again
- Ensure you're not exceeding reasonable usage limits

## File Structure

```
DD-webscraper/
├── scraper.py              # Main scraper script
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── urls.txt               # Example URLs file (optional)
├── .gitignore             # Git ignore rules
├── scraper_errors.log     # Error log (generated)
└── zillow_data_*.csv      # Output files (generated)
```

## Technical Details

### Dependencies
- **requests** (2.31.0): HTTP library for making web requests
- **beautifulsoup4** (4.12.2): HTML parsing library
- **lxml** (4.9.3): Fast XML/HTML parser for BeautifulSoup

### Data Extraction Methods

The scraper uses multiple fallback methods to extract each field:

1. **Address:** Looks for heading tags with address-related attributes
2. **Lot Size:** Searches for "Lot size" labels and nearby values
3. **Price:** Finds price-specific elements and validates dollar signs
4. **Price/sqft:** Looks for "$/sqft" patterns and related elements
5. **Days on Market:** Searches for "Time on Zillow" or similar phrases

### Limitations

- Only works with public Zillow listings (no authentication)
- Page structure changes may break extraction
- Some fields may not be available on all listings
- Cannot access "off-market" or "coming soon" listing data reliably
- Subject to Zillow's website availability and structure

## Contributing

This is a personal/educational tool. If you find bugs or have improvements:

1. Check if the issue is due to Zillow's page structure changing
2. Update the extraction methods in `scraper.py` accordingly
3. Test with multiple listing types (for sale, rental, etc.)

## License

Personal/Educational Use Only - Not for commercial use or redistribution.

## Version History

- **v1.0** (2025-11-08): Initial release
  - Single and batch URL scraping
  - CSV output with timestamps
  - Rate limiting and error handling
  - Comprehensive logging

## Support

For issues related to:
- **Python errors:** Check that dependencies are installed correctly
- **Scraping failures:** Check error log and Zillow's site structure
- **Feature requests:** This is a minimal viable tool; extend as needed

---

**Remember:** Always respect website terms of service and use web scraping responsibly.
