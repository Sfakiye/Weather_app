import os
from dbcm import DBCM
from scrape_weather import WeatherScraper
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), "weather.db")


class DBOperations:
    def __init__(self, db_name=DB_PATH):
        """
        Initialize database operations and ensure the required table exists.
        :param db_name: Name of the SQLite database file.
        """
        self.db_name = db_name
        self.initialize_db()

    def initialize_db(self):
        """
        Creates the weather_data table if it does not already exist.
        """
        with DBCM(self.db_name) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sample_date TEXT NOT NULL,
                    location TEXT NOT NULL,
                    min_temp REAL,
                    max_temp REAL,
                    avg_temp REAL,
                    UNIQUE(sample_date, location)
                )
            """)
    def save_data(self, weather_dict, location="Winnipeg"):
        """
        Saves weather data into the database while avoiding duplicate entries.
        :param weather_dict: Dictionary containing weather data with dates as
        keys and temperature values.
        :param location: Location name for the weather data (default: "Winnipeg").
        """
        with DBCM(self.db_name) as cursor:
            for date, temps in weather_dict.items():
                try:
                    cursor.execute('''INSERT INTO weather_data (sample_date,
                                   location, min_temp, max_temp, avg_temp)
                                      VALUES (?, ?, ?, ?, ?)''',
                                   (date, location, temps["Min"], temps["Max"], temps["Mean"]))
                except Exception:
                    print(f"Skipping duplicate entry for {date} in {location}.")
    def fetch_data(self, location="Winnipeg"):
        """
        Retrieves all weather data for a given location, ordered by date.
        :param location: Location name to filter weather data (default: "Winnipeg").
        :return: List of tuples containing weather records.
        """
        with DBCM(self.db_name) as cursor:
            cursor.execute('''SELECT * FROM weather_data WHERE location = ?
                           ORDER BY sample_date''', (location,))
            return cursor.fetchall()
    def purge_data(self):
        """
        Deletes all weather records from the database while keeping the table structure intact.
        """
        with DBCM(self.db_name) as cursor:
            cursor.execute("DELETE FROM weather_data")
def main():
    url = "https://climate.weather.gc.ca/climate_data/daily_data_e.html"
    scraper = WeatherScraper(url)
    current_date = datetime.today()
    current_year = current_date.year
    current_month = current_date.month
    data = scraper.fetch_weather_data(current_year, current_month, end_year=2022)
    try:
        database = DBOperations()
        database.save_data(data)
        print("Weather data saved successfully.")
    except Exception as e:
        print(f"Database operation failed: {e}")
    # Fetch and print all weather data from the database
    records = database.fetch_data()

    for record in records:
        print(record)
if __name__ == "__main__":
    main()
