import requests
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from datetime import datetime
class WeatherScraper(HTMLParser):
    """
    A web scraper to extract historical weather data from a given weather website.
    This class parses HTML tables containing weather data and stores it in a dictionary.
    """
    def __init__(self, base_url):
        """
        Initialize the WeatherScraper with the base URL.
        :param base_url: The base URL of the weather website.
        """
        super().__init__()
        self.base_url = base_url
        self.prev_month_url = None  # URL for navigating to the previous month's data
        self.is_prev_link = False  # Flag to detect the previous month navigation link
        self.weather_data = {}  # Dictionary to store extracted weather data
        self.in_table = False  # Flag to detect when inside a table element
        self.in_row = False  # Flag to detect when inside a row element
        self.in_td = False  # Flag to detect when inside a table cell
        self.current_data = []  # Temporary list to store row data
        self.valid_row = False  # Flag to determine if row contains valid data
        self.all_data = []  # List to store all extracted weather data
        self.col_index = 0  # Column index tracker
    def clean_url(self, base_url, href):
        """
        Cleans and constructs a URL by removing unnecessary query parameters.
        :param base_url: The base URL of the page.
        :param href: The relative URL to be cleaned.
        :return: A cleaned absolute URL without unnecessary parameters.
        """
        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)
        query_params = parse_qs(parsed_url.query)
        query_params.pop("Day", None)  # Remove 'Day' parameter to avoid redundant requests
        cleaned_query = urlencode(query_params, doseq=True)
        cleaned_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{cleaned_query}"
        return cleaned_url
    def handle_starttag(self, tag, attrs):
        """
        Handles the start of an HTML tag while parsing.
        Detects table elements, rows, cells, and navigation links.
        :param tag: The HTML tag being processed.
        :param attrs: The attributes associated with the tag.
        """
        attrs_dict = dict(attrs)
        if tag == 'li' and attrs_dict.get('id') == 'nav-prev1':
            self.is_prev_link = True
        if self.is_prev_link and tag == 'a' and 'href' in attrs_dict:
            self.prev_month_url = self.clean_url(self.base_url, attrs_dict['href'])
        if tag == "table":
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.in_row = True
            self.col_index = 0
            self.current_data = []
            self.valid_row = False
        elif self.in_row and tag == "td":
            self.in_td = True
    def handle_endtag(self, tag):
        """
        Handles the closing of an HTML tag.
        :param tag: The HTML tag being closed.
        """
        if tag == "table":
            self.in_table = False
        elif tag == "tr":
            if self.valid_row and len(self.current_data) >= 3:
                self.all_data.append(self.current_data.copy())
            self.in_row = False
        elif tag == "td":
            self.in_td = False
        if tag == 'li' and self.is_prev_link:
            self.is_prev_link = False
    def handle_data(self, data):
        """
        Processes textual data inside table cells.
        Extracts numerical values representing temperature data.
        :param data: The data inside an HTML element.
        """
        if self.in_td:
            data = data.strip()
            if data.replace(".", "").replace("-", "").isdigit():
                if self.col_index < 3:
                    self.current_data.append(float(data))
                    self.valid_row = True
                self.col_index += 1
    def fetch_weather_data(self, start_year, start_month, end_year=None, end_month=None):
        year, month = start_year, start_month
        try:
            while True:
                print(f"Scraping data for {year}-{month:02d}...")
                self.all_data = []
                url = f"{self.base_url}?StationID=27174&timeframe=2&StartYear=1840&EndYear=2025&Year={year}&Month={month}"
                
                # Request weather data for the given year and month
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(f"[ERROR] Request failed for {year}-{month:02d}: {e}")
                    break

                # Handle "No data available" case
                if "No data available" in response.text:
                    print(f"[INFO] No data available for {year}-{month:02d}.")
                    break

                # Process the HTML content
                try:
                    self.feed(response.text)
                except Exception as e:
                    print(f"[ERROR] Failed to parse HTML for {year}-{month:02d}: {e}")
                    break

                # Store weather data
                for i, data_row in enumerate(self.all_data[:-3]):  # Exclude last three rows (footer or non-data rows)
                    try:
                        date_str = f"{year}-{month:02d}-{i+1:02d}"
                        self.weather_data[date_str] = {
                            "Max": data_row[0],
                            "Min": data_row[1],
                            "Mean": data_row[2],
                        }
                    except (IndexError, ValueError) as e:
                        print(f"[WARNING] Skipped malformed row on {year}-{month:02d}-{i+1:02d}: {e}")

                # Check if we've reached the end of the desired period
                if end_year is not None and end_month is not None:
                    if year == end_year and month == end_month:
                        print(f"[INFO] Reached specified end date: {end_year}-{end_month:02d}")
                        break

                # Move to the previous month
                if month == 1:
                    year -= 1
                    month = 12
                else:
                    month -= 1

                # Stop scraping if no more previous data exists
                if self.prev_month_url == url:
                    print(f"[INFO] Stopping scrape: No more weather data beyond {year}-{month:02d}")
                    break

        except KeyboardInterrupt:
            print("\n[INFO] Scraping interrupted by user.")
        
        return self.weather_data

def main():
    url = "https://climate.weather.gc.ca/climate_data/daily_data_e.html"
    scraper = WeatherScraper(url)
    current_date = datetime.today()
    current_year = current_date.year
    current_month = current_date.month
    data = scraper.fetch_weather_data(current_year, current_month, end_year=2020,end_month=1)
    for date,values in data.items():
        print(date,":", values)
if __name__ == "__main__":
    main()