"""Weather Data Processing Script.
This script fetches, stores, updates, and visualizes weather data for Winnipeg.
It interacts with a database and provides functionality for downloading historical 
data, updating records, and generating visualizations.
"""
from datetime import datetime,date,timedelta
import logging
import os
from tabulate import tabulate  # For tabular data display
from db_operations import DBOperations
from scrape_weather import WeatherScraper
from plot_operations import PlotOperations
# Set up logging configuration in the current directory
# Set up logging configuration in the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(script_dir, "weather_process.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
class WeatherProcessor:
    """Handles fetching, storing, updating, and visualizing weather data."""
    def __init__(self):
        """Initializes WeatherProcessor with database, scraper, and plotter."""
        url = "https://climate.weather.gc.ca/climate_data/daily_data_e.html"
        self.db = DBOperations("weather.db")
        self.scraper = WeatherScraper(base_url=url)
        self.plotter = PlotOperations()
    def download_full_weather_data(self):
        """Downloads and stores historical weather data from 1997 onwards."""
        try:
            print("Downloading data...")
            current_date = datetime.today()
            current_year = current_date.year
            current_month = current_date.month
            end_year= int(input( 'Enter weather data end year: '))
            weather_data = self.scraper.fetch_weather_data(current_year, current_month, end_year=end_year)
            self.db.save_data(weather_data)
            print("Weather data successfully downloaded and stored.")
        except Exception as error:
            logging.error("Error downloading full weather data: %s", error)     
    def get_latest_date_from_db(self):
        try:
            data = self.db.fetch_data()
            logging.info("Fetched %d records from DB.", len(data))
            if not data:
                return None
            latest_date = max(record[1] for record in data if record[1])
            return datetime.strptime(latest_date, "%Y-%m-%d").date()
        except Exception as error:
            logging.error("Error retrieving latest date from database: %s", error, exc_info=True)
            return None
    def update_weather_data(self):
        """Updates the weather data in the database if new data is available."""
        try:
            today = datetime.today().date()
            latest_date = self.get_latest_date_from_db()

            print(f"Today's date: {today}")
            print(f"Latest date in DB: {latest_date}")

            if latest_date is None:
                print("No data found in database. Downloading full dataset...")
                self.download_full_weather_data()
                return

            # Adjusted check to avoid scraping data that hasn't been published yet
            if latest_date >= today - timedelta(days=1):
                print("Database is already up to date or waiting for today's data to become available.")
                return
            print(f"Updating data from {latest_date + timedelta(days=1)} to {today}...")
            start = latest_date + timedelta(days=1)
            end = today
            all_new_data = []
            current = start.replace(day=1)
            last = end.replace(day=1)
            while current <= last:
                year, month = current.year, current.month
                print(f"Fetching data for {year}-{month:02d}...")
                monthly_data = self.scraper.fetch_weather_data(year, month, end_year=year)
                # Filter only the missing dates
                filtered = [
                    row for row in monthly_data
                    if start <= datetime.strptime(row[1], "%Y-%m-%d").date() <= end
                ]
                all_new_data.extend(filtered)
                # Move to next month
                next_month = current.replace(day=28) + timedelta(days=4)
                current = next_month.replace(day=1)
            if all_new_data:
                self.db.save_data(all_new_data)
                print(f"Database updated with {len(all_new_data)} new records!")
            else:
                print("No new records found.")
        except Exception as error:
            print("Error updating weather data.")
            logging.error("Error updating weather data: %s", error, exc_info=True)
    def view_weather_data(self):
        """Displays stored weather data in tabular format."""
        try:
            location = input("Enter location (default: Winnipeg): ") or "Winnipeg"
            records = self.db.fetch_data(location)
            if not records:
                print("No weather data available.")
                return
            headers = ["ID", "Date", "Location", "Max Temp", "Min Temp", "Mean Temp"]
            print(tabulate(records, headers=headers, tablefmt="grid"))
        except Exception as error:
            logging.error("Error displaying weather data: %s", error)
    def generate_boxplot(self):
        """Generates a box plot of weather trends over selected years."""
        try:
            start_year = int(input("Enter the start year for box plot: "))
            end_year = int(input("Enter the end year for box plot: "))
            location = input("Enter the location (default: Winnipeg): ") or "Winnipeg"
            weather_data = {month: [] for month in range(1, 13)}
            records = self.db.fetch_data(location)
            for record in records:
                date = record[1]
                mean_temp = record[5]
                year, month, _ = map(int, date.split('-'))
                if start_year <= year <= end_year:
                    weather_data[month].append(mean_temp)
            self.plotter.plot_boxplot(weather_data)
        except Exception as error:
            logging.error("Error generating box plot: %s", error)
    def generate_lineplot(self):
        """Generates a line plot for daily temperatures of a selected month."""
        try:
            year = int(input("Enter the year for the line plot: "))
            month = int(input("Enter the month (1-12) for the line plot: "))
            location = input("Enter the location (default: Winnipeg): ") or "Winnipeg"
            days, temperatures = [], []
            records = self.db.fetch_data(location)
            for record in records:
                date = record[1]
                mean_temp = record[5]
                rec_year, rec_month, day = map(int, date.split('-'))
                if rec_year == year and rec_month == month:
                    days.append(day)
                    temperatures.append(mean_temp)
            if days and temperatures:
                self.plotter.plot_lineplot(days, temperatures, month, year)
            else:
                print("No data available for the selected month and year.")
        except Exception as error:
            logging.error("Error generating line plot: %s", error)
    def menu(self):
        """Displays the main menu and handles user input."""
        while True:
            print("\nWinnipeg Weather Data Processor")
            print("1. Download full weather data")
            print("2. Update weather data")
            print("3. View weather data")
            print("4. Generate box plot (Yearly trends)")
            print("5. Generate line plot (Daily temperatures)")
            print("6. Exit")
            choice = input("Enter your choice: ")
            if choice == "1":
                self.download_full_weather_data()
            elif choice == "2":
                self.update_weather_data()
            elif choice == "3":
                self.view_weather_data()
            elif choice == "4":
                self.generate_boxplot()
            elif choice == "5":
                self.generate_lineplot()
            elif choice == "6":
                print("Exiting program...")
                break
            else:
                print("Invalid choice. Please try again.")
if __name__ == "__main__":
    PROCESSOR = WeatherProcessor()
    PROCESSOR.menu()