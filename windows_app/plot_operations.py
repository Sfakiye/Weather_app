import matplotlib.pyplot as plt
from db_operations import DBOperations
import os

class PlotOperations:
    """
    Handles plotting operations for visualizing weather data.
    """
    def plot_boxplot(self, weather_data):
        plt.figure(figsize=(10, 6))
        plt.boxplot([weather_data.get(month, []) for month in range(1, 13)], 
                    labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        plt.xlabel("Month")
        plt.ylabel("Mean Temperature (°C)")
        plt.title("Monthly Mean Temperature Distribution")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    def plot_lineplot(self, days, temperatures, month, year):
        plt.figure(figsize=(10, 6))
        plt.plot(days, temperatures, marker='o', linestyle='-', label="Mean Temperature")
        plt.xlabel("Day")
        plt.ylabel("Mean Temperature (°C)")
        plt.title(f"Daily Mean Temperatures - {month}/{year}")
        plt.xticks(days, rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
def main():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "weather.db")
    db = DBOperations(db_path)
    plotter = PlotOperations()
    try:
        start_year = int(input("Enter the start year for box plot (e.g. 2020): "))
        end_year = int(input("Enter the end year for box plot (e.g. 2024): "))
        location = input("Enter the location (default: Winnipeg): ") or "Winnipeg"
        records = db.fetch_data(location)
        
        weather_data = {m: [] for m in range(1, 13)}
        for record in records:
            date = record[1]
            mean_temp = record[5]
            year, m, _ = map(int, date.split('-'))
            if start_year <= year <= end_year:
                weather_data[m].append(mean_temp)
        if any(weather_data.values()):
            plotter.plot_boxplot(weather_data)
        else:
            print("No data available for the selected month and year.")
    except Exception as error:
        print("Error generating box plot:", error)
    try:
        year = int(input("Enter the year for the line plot (e.g. 2023): "))
        selected_month = int(input("Enter the month (1-12) for the line plot: "))
        location = input("Enter the location (default: Winnipeg): ") or "Winnipeg"
        records = db.fetch_data(location)
        days, temperatures = [], []
        for record in records:
            date = record[1]
            mean_temp = record[5]
            rec_year, rec_month, day = map(int, date.split('-'))
            if rec_year == year and rec_month == selected_month:
                days.append(day)
                temperatures.append(mean_temp)
        if days and temperatures:
            plotter.plot_lineplot(days, temperatures, selected_month, year)
        else:
            print("No data available for the selected month and year.")
    except Exception as error:
        print("Error generating line plot:", error)
if __name__ == "__main__":
    main()