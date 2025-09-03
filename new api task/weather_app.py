import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import json
import os

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)
        
        # API Configuration - Replace with your actual API key
        self.api_key = "60a79277bc337c9c1b457a7b9fa56966"  # Get from https://openweathermap.org/api
        self.base_url = "http://api.openweathermap.org/data/2.5/"
        
        # Create UI
        self.create_widgets()
        
        # Load last searched city if available
        self.load_last_city()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Weather App", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)
        
        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        self.city_var = tk.StringVar()
        city_entry = ttk.Entry(search_frame, textvariable=self.city_var, font=("Arial", 12))
        city_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        city_entry.bind("<Return>", lambda e: self.get_weather())
        
        search_btn = ttk.Button(search_frame, text="Search", command=self.get_weather)
        search_btn.pack(side=tk.RIGHT)
        
        # Current weather frame
        self.current_frame = ttk.LabelFrame(main_frame, text="Current Weather", padding=10)
        self.current_frame.pack(fill=tk.X, pady=10)
        
        # Forecast frame
        self.forecast_frame = ttk.LabelFrame(main_frame, text="5-Day Forecast", padding=10)
        self.forecast_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Forecast container with canvas and scrollbar
        self.forecast_canvas = tk.Canvas(self.forecast_frame, bg="white", height=250)
        self.scrollbar = ttk.Scrollbar(self.forecast_frame, orient="vertical", command=self.forecast_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.forecast_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.forecast_canvas.configure(scrollregion=self.forecast_canvas.bbox("all"))
        )
        
        self.forecast_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.forecast_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.forecast_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def get_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showerror("Error", "Please enter a city name")
            return
        
        self.status_var.set("Fetching weather data...")
        self.root.update()
        
        try:
            # Get current weather
            current_url = f"{self.base_url}weather?q={city}&appid={self.api_key}&units=metric"
            current_response = requests.get(current_url)
            current_data = current_response.json()
            
            if current_response.status_code != 200:
                messagebox.showerror("Error", f"Could not retrieve data: {current_data.get('message', 'Unknown error')}")
                self.status_var.set("Error fetching data")
                return
            
            # Get forecast
            forecast_url = f"{self.base_url}forecast?q={city}&appid={self.api_key}&units=metric"
            forecast_response = requests.get(forecast_url)
            forecast_data = forecast_response.json()
            
            if forecast_response.status_code != 200:
                messagebox.showerror("Error", f"Could not retrieve forecast: {forecast_data.get('message', 'Unknown error')}")
                self.status_var.set("Error fetching forecast")
                return
            
            # Update UI with weather data
            self.display_current_weather(current_data)
            self.display_forecast(forecast_data)
            
            # Save this city as last searched
            self.save_last_city(city)
            
            self.status_var.set(f"Weather data for {city} loaded successfully")
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")
            self.status_var.set("Network error occurred")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error processing data")
    
    def display_current_weather(self, data):
        # Clear previous data
        for widget in self.current_frame.winfo_children():
            widget.destroy()
        
        # Display current weather
        city_name = data.get('name', 'Unknown')
        country = data.get('sys', {}).get('country', '')
        temp = data.get('main', {}).get('temp', 0)
        feels_like = data.get('main', {}).get('feels_like', 0)
        humidity = data.get('main', {}).get('humidity', 0)
        pressure = data.get('main', {}).get('pressure', 0)
        wind_speed = data.get('wind', {}).get('speed', 0)
        description = data.get('weather', [{}])[0].get('description', '').title()
        icon_code = data.get('weather', [{}])[0].get('icon', '')
        
        # City name and description
        ttk.Label(self.current_frame, text=f"{city_name}, {country}", font=("Arial", 16, "bold")).pack(anchor=tk.W)
        ttk.Label(self.current_frame, text=description, font=("Arial", 12)).pack(anchor=tk.W)
        
        # Temperature
        temp_frame = ttk.Frame(self.current_frame)
        temp_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(temp_frame, text=f"{temp:.1f}°C", font=("Arial", 24, "bold")).pack(side=tk.LEFT)
        ttk.Label(temp_frame, text=f"Feels like: {feels_like:.1f}°C").pack(side=tk.LEFT, padx=(20, 0))
        
        # Additional info
        info_frame = ttk.Frame(self.current_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"Humidity: {humidity}%").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Pressure: {pressure} hPa").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Wind: {wind_speed} m/s").pack(anchor=tk.W)
    
    def display_forecast(self, data):
        # Clear previous forecast
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Group forecasts by day
        forecasts = {}
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            if date not in forecasts:
                forecasts[date] = []
            forecasts[date].append(item)
        
        # Display forecast for next 5 days
        for i, (date, items) in enumerate(list(forecasts.items())[:5]):
            day_frame = ttk.Frame(self.scrollable_frame, relief=tk.RAISED, borderwidth=1)
            day_frame.pack(fill=tk.X, pady=2, padx=2)
            
            # Date header
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            ttk.Label(day_frame, text=date_obj.strftime('%A, %b %d'), 
                     font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=2)
            
            # Forecast details
            details_frame = ttk.Frame(day_frame)
            details_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Use noon forecast or closest available
            noon_forecast = min(items, key=lambda x: abs(12 - datetime.fromtimestamp(x['dt']).hour))
            
            temp = noon_forecast['main']['temp']
            description = noon_forecast['weather'][0]['description'].title()
            humidity = noon_forecast['main']['humidity']
            
            ttk.Label(details_frame, text=f"Day: {temp:.1f}°C", width=15).pack(side=tk.LEFT)
            ttk.Label(details_frame, text=description, width=20).pack(side=tk.LEFT)
            ttk.Label(details_frame, text=f"Humidity: {humidity}%").pack(side=tk.LEFT)
    
    def save_last_city(self, city):
        """Save the last searched city to a file"""
        try:
            with open("weather_app_prefs.json", "w") as f:
                json.dump({"last_city": city}, f)
        except:
            pass  # Silently fail if we can't save preferences
    
    def load_last_city(self):
        """Load the last searched city from file"""
        try:
            if os.path.exists("weather_app_prefs.json"):
                with open("weather_app_prefs.json", "r") as f:
                    prefs = json.load(f)
                    self.city_var.set(prefs.get("last_city", ""))
        except:
            pass  # Silently fail if we can't load preferences

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()