#!/usr/bin/env python3
"""
Zillow Property Data Scraper
-----------------------------
Personal educational use only. This tool scrapes property data from Zillow listings.
Use responsibly and in accordance with Zillow's Terms of Service.

Author: Personal Use Tool
License: Educational/Personal Use Only
"""

import requests
from bs4 import BeautifulSoup
import csv
import argparse
import time
import random
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_errors.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# Realistic browser user agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'

# Request timeout in seconds
REQUEST_TIMEOUT = 30

# Rate limiting: random delay between requests (in seconds)
MIN_DELAY = 5
MAX_DELAY = 8

# Maximum recommended URLs per execution
MAX_URLS_WARNING = 20


class ZillowScraper:
    """Scraper for extracting property data from Zillow listings."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def validate_url(self, url):
        """Validate that URL is a Zillow domain."""
        try:
            parsed = urlparse(url)
            return 'zillow.com' in parsed.netloc.lower()
        except:
            return False

    def extract_property_data(self, url):
        """
        Extract property data from a Zillow listing URL.

        Returns:
            dict: Property data with keys: url, address, lot_size, price,
                  price_per_sqft, days_on_market, scrape_timestamp, error
        """
        result = {
            'url': url,
            'address': 'N/A',
            'lot_size': 'N/A',
            'price': 'N/A',
            'price_per_sqft': 'N/A',
            'days_on_market': 'N/A',
            'scrape_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': None
        }

        if not self.validate_url(url):
            result['error'] = 'Invalid Zillow URL'
            logger.warning(f"Invalid URL: {url}")
            return result

        try:
            # Fetch the page
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract address
            result['address'] = self._extract_address(soup)

            # Extract lot size
            result['lot_size'] = self._extract_lot_size(soup)

            # Extract price
            result['price'] = self._extract_price(soup)

            # Extract price per sqft
            result['price_per_sqft'] = self._extract_price_per_sqft(soup)

            # Extract days on market
            result['days_on_market'] = self._extract_days_on_market(soup)

            logger.info(f"Successfully scraped: {result['address']}")

        except requests.exceptions.Timeout:
            result['error'] = 'Request timeout'
            logger.error(f"Timeout for URL: {url}")
        except requests.exceptions.HTTPError as e:
            result['error'] = f'HTTP {e.response.status_code}'
            logger.error(f"HTTP error for URL: {url} - {e}")
        except requests.exceptions.RequestException as e:
            result['error'] = f'Request failed: {str(e)}'
            logger.error(f"Request failed for URL: {url} - {e}")
        except Exception as e:
            result['error'] = f'Parsing error: {str(e)}'
            logger.error(f"Parsing error for URL: {url} - {e}")

        return result

    def _extract_address(self, soup):
        """Extract property address from page."""
        # Try multiple selectors for address
        selectors = [
            ('h1', {'class': 'ds-address-container'}),
            ('h1', {'data-testid': 'bdp-address'}),
            ('h1', {}),  # Fallback to first h1
        ]

        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                address_text = element.get_text(strip=True)
                if address_text:
                    return address_text

        return 'N/A'

    def _extract_lot_size(self, soup):
        """Extract lot size from page."""
        # Look for lot size in various places
        try:
            # Method 1: Look in facts and features section
            lot_keywords = ['Lot size', 'Lot Size', 'lot size']
            for keyword in lot_keywords:
                spans = soup.find_all('span', string=lambda text: text and keyword in text)
                for span in spans:
                    # Look for value in nearby elements
                    parent = span.find_parent()
                    if parent:
                        next_span = parent.find_next('span')
                        if next_span:
                            lot_text = next_span.get_text(strip=True)
                            if lot_text and lot_text != keyword:
                                return lot_text

            # Method 2: Look in data attributes or structured data
            # This might need adjustment based on actual page structure
            facts = soup.find_all('span', {'data-testid': lambda x: x and 'lot' in x.lower() if x else False})
            for fact in facts:
                text = fact.get_text(strip=True)
                if any(unit in text.lower() for unit in ['sqft', 'sq ft', 'acres', 'acre']):
                    return text

        except Exception as e:
            logger.debug(f"Error extracting lot size: {e}")

        return 'N/A'

    def _extract_price(self, soup):
        """Extract listing price from page."""
        try:
            # Look for price in various selectors
            selectors = [
                ('span', {'data-testid': 'price'}),
                ('span', {'class': lambda x: x and 'price' in x.lower() if x else False}),
                ('div', {'class': lambda x: x and 'price' in x.lower() if x else False}),
            ]

            for tag, attrs in selectors:
                element = soup.find(tag, attrs)
                if element:
                    price_text = element.get_text(strip=True)
                    if price_text and '$' in price_text:
                        return price_text

            # Try to find any element with dollar sign and large number
            all_text = soup.find_all(string=lambda text: text and '$' in text and any(c.isdigit() for c in text))
            for text in all_text:
                text = text.strip()
                # Look for price patterns like $XXX,XXX
                if text.startswith('$') and ',' in text:
                    return text.split()[0]  # Take first word to avoid descriptions

        except Exception as e:
            logger.debug(f"Error extracting price: {e}")

        return 'N/A'

    def _extract_price_per_sqft(self, soup):
        """Extract price per square foot from page."""
        try:
            # Look for price per sqft patterns
            patterns = ['$/sqft', 'per sqft', 'Price/sqft']

            for pattern in patterns:
                spans = soup.find_all('span', string=lambda text: text and pattern.lower() in text.lower() if text else False)
                for span in spans:
                    parent = span.find_parent()
                    if parent:
                        # Look for adjacent value
                        for sibling in parent.find_next_siblings():
                            text = sibling.get_text(strip=True)
                            if text and '$' in text:
                                return text
                        # Or previous sibling
                        prev = parent.find_previous_sibling()
                        if prev:
                            text = prev.get_text(strip=True)
                            if text and '$' in text:
                                return text

            # Alternative: look for specific data attributes
            price_sqft_elem = soup.find('span', {'data-testid': lambda x: x and 'price-per-sqft' in x.lower() if x else False})
            if price_sqft_elem:
                return price_sqft_elem.get_text(strip=True)

        except Exception as e:
            logger.debug(f"Error extracting price per sqft: {e}")

        return 'N/A'

    def _extract_days_on_market(self, soup):
        """Extract days on market from page."""
        try:
            # Look for "Time on Zillow" or "Days on Market"
            keywords = ['Time on Zillow', 'Days on Zillow', 'on Zillow', 'Days on market']

            for keyword in keywords:
                elements = soup.find_all(string=lambda text: text and keyword.lower() in text.lower() if text else False)
                for elem in elements:
                    # Look for parent and nearby elements
                    parent = elem.find_parent() if hasattr(elem, 'find_parent') else None
                    if parent:
                        # Get all text from parent
                        full_text = parent.get_text(strip=True)
                        # Extract number of days
                        words = full_text.split()
                        for i, word in enumerate(words):
                            if word.isdigit() or (word.replace(',', '').isdigit()):
                                # Check if next word is "day" or "days"
                                if i + 1 < len(words) and 'day' in words[i + 1].lower():
                                    return f"{word} days"
                                # Or if it just has a number before "on Zillow"
                                elif 'zillow' in full_text.lower() or 'market' in full_text.lower():
                                    return f"{word} days"

        except Exception as e:
            logger.debug(f"Error extracting days on market: {e}")

        return 'N/A'

    def scrape_urls(self, urls, output_file, append=False):
        """
        Scrape multiple URLs and save to CSV.

        Args:
            urls: List of Zillow URLs to scrape
            output_file: Path to output CSV file
            append: Whether to append to existing file or create new
        """
        # Warn if too many URLs
        if len(urls) > MAX_URLS_WARNING:
            print(f"\n⚠️  WARNING: You are attempting to scrape {len(urls)} URLs.")
            print(f"   Recommended maximum is {MAX_URLS_WARNING} URLs per execution.")
            print(f"   This will take approximately {len(urls) * ((MIN_DELAY + MAX_DELAY) / 2) / 60:.1f} minutes.")
            response = input("   Continue? (y/n): ")
            if response.lower() != 'y':
                print("Aborted by user.")
                sys.exit(0)

        # Prepare output file
        mode = 'a' if append and Path(output_file).exists() else 'w'
        write_header = mode == 'w' or not Path(output_file).exists()

        results = []
        failed_count = 0

        print(f"\nStarting scrape of {len(urls)} URL(s)...")
        print(f"Output file: {output_file}")
        print("-" * 60)

        for i, url in enumerate(urls, 1):
            print(f"\nProcessing {i}/{len(urls)}: {url[:60]}...")

            # Scrape the URL
            result = self.extract_property_data(url)
            results.append(result)

            if result['error']:
                failed_count += 1
                print(f"  ❌ Failed: {result['error']}")
            else:
                print(f"  ✓ Success: {result['address']}")
                print(f"    Price: {result['price']} | Lot: {result['lot_size']}")

            # Write to CSV incrementally
            with open(output_file, mode, newline='', encoding='utf-8') as f:
                fieldnames = ['url', 'address', 'lot_size', 'price', 'price_per_sqft',
                            'days_on_market', 'scrape_timestamp', 'error']
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                if write_header:
                    writer.writeheader()
                    write_header = False

                writer.writerow(result)

            # Rate limiting: sleep between requests (except for last one)
            if i < len(urls):
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                print(f"  ⏱  Waiting {delay:.1f}s before next request...")
                time.sleep(delay)

        # Print summary
        print("\n" + "=" * 60)
        print("SCRAPING COMPLETE")
        print("=" * 60)
        print(f"Total URLs processed: {len(urls)}")
        print(f"Successful: {len(urls) - failed_count}")
        print(f"Failed: {failed_count}")
        print(f"Success rate: {(len(urls) - failed_count) / len(urls) * 100:.1f}%")
        print(f"\nResults saved to: {output_file}")
        if failed_count > 0:
            print(f"Error details logged to: scraper_errors.log")
        print("=" * 60)


def read_urls_from_file(file_path):
    """Read URLs from a text file (one per line)."""
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        return urls
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the scraper."""
    parser = argparse.ArgumentParser(
        description='Zillow Property Data Scraper - For personal educational use only',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single URL
  python scraper.py "https://www.zillow.com/homedetails/..."

  # Scrape multiple URLs from file
  python scraper.py --file urls.txt

  # Custom output filename
  python scraper.py --file urls.txt --output my_results.csv

  # Append to existing CSV
  python scraper.py --file urls.txt --append
        """
    )

    # URL input options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('url', nargs='?', help='Single Zillow listing URL to scrape')
    group.add_argument('--file', '-f', help='Path to text file containing URLs (one per line)')

    # Output options
    parser.add_argument('--output', '-o', help='Output CSV filename (default: timestamped)')
    parser.add_argument('--append', '-a', action='store_true',
                       help='Append to existing output file instead of creating new')

    args = parser.parse_args()

    # Gather URLs
    if args.url:
        urls = [args.url]
    else:
        urls = read_urls_from_file(args.file)

    if not urls:
        print("Error: No URLs to process")
        sys.exit(1)

    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        output_file = f'zillow_data_{timestamp}.csv'

    # Run scraper
    scraper = ZillowScraper()
    scraper.scrape_urls(urls, output_file, append=args.append)


if __name__ == '__main__':
    main()
