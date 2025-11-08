# Zillow Property Data Scraper

## Objective
Build a Python command-line tool that scrapes property data from Zillow listing URLs for personal use.

## Requirements

### Data to Extract
From each Zillow listing URL, extract:
1. **Address** (full property address)
2. **Lot Size** (in sqft or acres)
3. **Price** (listing price)
4. **Price per sqft** 
5. **Days on Market**

### Input Method
- Accept Zillow listing URLs (not addresses)
- Support two input modes:
  1. Single URL via command-line argument: `python scraper.py "https://zillow.com/..."`
  2. Multiple URLs from text file: `python scraper.py --file urls.txt`

### Output
- Save results to CSV file with columns: URL, Address, Lot_Size, Price, Price_Per_Sqft, Days_On_Market, Scrape_Timestamp
- Include error handling column for failed scrapes
- Print progress to console as it runs

## Technical Specifications

### Core Libraries
- `requests` or `httpx` for HTTP requests
- `BeautifulSoup4` (bs4) for HTML parsing
- `csv` for output
- `argparse` for command-line interface
- `time` for delays

### Best Practices (Critical for Personal Use)

**Rate Limiting:**
- Add 5-8 second random delay between requests
- Max ~20 URLs per execution (warn user if more)
- Use realistic User-Agent header

**Error Handling:**
- Handle missing data gracefully (mark as "N/A")
- Catch HTTP errors (404, 403, timeouts)
- Continue processing remaining URLs if one fails
- Log errors to separate error log file

**Respectful Scraping:**
- Single-threaded (no parallel requests)
- Timeout after 30 seconds per request
- Don't retry failed requests automatically

## Features

### Must Have
- Read URLs from command line or file
- Extract all 5 data points
- Save to timestamped CSV file (e.g., `zillow_data_2025-11-07_14-30.csv`)
- Progress indicator ("Processing 3/10...")
- Error summary at end

### Nice to Have
- Validate URLs are Zillow domains before scraping
- Handle both old and new Zillow URL formats
- Summary statistics (success rate, total found)
- Option to append to existing CSV instead of creating new file

## Code Structure
```
zillow-scraper/
├── scraper.py          # Main script
├── requirements.txt    # Dependencies
├── README.md          # Usage instructions
└── .gitignore         # Ignore output files
```

## Expected Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Single URL
python scraper.py "https://www.zillow.com/homedetails/..."

# Multiple URLs from file
python scraper.py --file urls.txt

# With custom output filename
python scraper.py --file urls.txt --output my_results.csv
```

## Important Notes

1. **Legal Disclaimer**: Add comment in code noting this is for personal educational use only
2. **Volume Warning**: If input file has >20 URLs, warn user and ask for confirmation
3. **Data Availability**: Some fields may not exist on all listings - handle gracefully
4. **No Storage**: Don't cache/store HTML - respect Zillow's ToS
5. **User Agent**: Use a realistic browser user agent string

## Testing
Include 2-3 example Zillow URLs in README for testing purposes.

## Deliverables
1. Working Python script
2. requirements.txt with all dependencies
3. README.md with clear usage instructions and examples
4. Sample urls.txt with 2-3 test URLs

## Questions to Resolve During Build
- Should we validate that URLs are actually Zillow domains?
- How to handle properties with multiple lot size formats (acres vs sqft)?
- Should we save failed URLs to a separate file for retry?
