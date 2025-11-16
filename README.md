# 🌦️ WeatherApp — Real-Time Weather Fetching & Visualization

WeatherApp is a lightweight Python application that automatically **fetches, stores, updates, and visualizes** weather data for *Winnipeg*. It uses web scraping, a local SQLite database, and plotting tools to track temperature trends over time.

> ⚠️ **Project Status:**  
> This project is **currently under active development**.  
> The version uploaded to this repository represents **Milestone One**, which includes the basic scraping and storage functionality.

---

## ✨ Features (Milestone One)

- 📥 **Automatic weather scraping** from an online source  
- 🗂️ **Local SQLite database** (`weather.db`) for storing daily weather data  
- 🔄 **Duplicate-entry protection** when updating records  
- 📊 **Basic temperature visualization**  
- 📝 **Process logging** via `weather_process.log`  
- 🖥️ **Windows executable** included (`WeatherAppInstaller.exe`)

---

## 🚀 How It Works

1. Scrapes the latest weather information for Winnipeg.  
2. Saves or updates weather data in the SQLite database.  
3. Generates basic plots using Matplotlib.  
4. Logs all operations for debugging and transparency.

---

## 🛠️ Technologies Used

- Python  
- BeautifulSoup (Web Scraping)  
- SQLite  
- Matplotlib  
- PyInstaller (for creating the standalone executable)

---

## 👥 Contributors

- **Samson Fakiye**  
- **Tamana Singh**

---

## 📦 Installation

Download and run:


