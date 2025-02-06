from flask import Flask, render_template, request, jsonify
import phonenumbers
from phonenumbers import geocoder, carrier
from opencage.geocoder import OpenCageGeocode
import folium
import requests
import random

app = Flask(__name__)

# Your OpenCage API Key (Get it free from https://opencagedata.com/)
OPENCAGE_API_KEY = "56ad04481db1431aa77386781c9398bc"

# Mock Call Data (Replace with real database in production)
frequent_callers = {
    "+919876543210": ["+911234567890", "+919876543211", "+919812345678"],
    "+919876543211": ["+911111111111", "+911222222222", "+911333333333"],
}

def get_number_details(phone_number):
    """Fetches details for a given phone number."""
    parsed_number = phonenumbers.parse(phone_number)
    
    # General location
    location = geocoder.description_for_number(parsed_number, "en")
    
    # Service provider
    service_provider = carrier.name_for_number(parsed_number, "en")
    
    # Get coordinates from OpenCage
    geocoder_api = OpenCageGeocode(OPENCAGE_API_KEY)
    result = geocoder_api.geocode(location)
    
    if result:
        lat, lng = result[0]['geometry']['lat'], result[0]['geometry']['lng']
    else:
        lat, lng = None, None

    return {
        "location": location,
        "service_provider": service_provider,
        "coordinates": (lat, lng) if lat and lng else None,
    }

def get_live_location():
    """Fetches the user's live location using an IP-based geolocation API."""
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        loc = data["loc"].split(",")
        return {
            "city": data["city"],
            "region": data["region"],
            "country": data["country"],
            "coordinates": (float(loc[0]), float(loc[1])),
        }
    except:
        return None

@app.route("/", methods=["GET", "POST"])
def home():
    """Handles the frontend interface."""
    if request.method == "POST":
        phone_number = request.form["phone_number"]
        details = get_number_details(phone_number)
        live_location = get_live_location()
        
        # Get 10 most frequent callers
        top_callers = frequent_callers.get(phone_number, ["No Data"] * 10)
        
        return render_template("index.html", phone_number=phone_number, details=details, 
                               live_location=live_location, top_callers=top_callers)

    return render_template("index.html")

@app.route("/map/<lat>/<lng>")
def show_map(lat, lng):
    """Generates an interactive Google Map link."""
    map_url = f"https://www.google.com/maps?q={lat},{lng}"
    return f'<h2>View Location: <a href="{map_url}" target="_blank">Open in Google Maps</a></h2>'

if __name__ == "__main__":
    app.run(debug=True)
