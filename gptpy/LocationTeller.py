#!/usr/bin/env python3
import requests

def get_location():
    response = requests.get("http://ip-api.com/json/")
    data = response.json()
    if data["status"] == "success":
        print("Country:", data["country"])
        print("Region:", data["regionName"])
        print("City:", data["city"])
        print("ZIP:", data["zip"])
        print("Latitude:", data["lat"])
        print("Longitude:", data["lon"])
    else:
        print("Location not found")

if __name__ == "__main__":
    get_location()