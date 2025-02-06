import folium
import phonenumbers
from phonenumbers import geocoder, carrier
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

def get_location(phone_number):
    """Get general location, service provider, and coordinates."""
    parsed_number = phonenumbers.parse(phone_number, "US")
    location = geocoder.description_for_number(parsed_number, "en")
    service_provider = carrier.name_for_number(parsed_number, "en")
    
    # Get coordinates using API (Replace with actual API key)
    api_key = "YOUR_API_KEY"
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={api_key}"
    response = requests.get(url).json()
    lat, lng = response["results"][0]["geometry"].values()
    
    return location, service_provider, lat, lng

def generate_map(lat, lng, filename="map.html"):
    """Generate a Google Maps view of the location."""
    map_object = folium.Map(location=[lat, lng], zoom_start=15)
    folium.Marker([lat, lng], popup="Phone Location", tooltip="Click to see location").add_to(map_object)
    map_object.save(filename)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        phone_number = request.form["phone_number"]
        location, service_provider, lat, lng = get_location(phone_number)
        generate_map(lat, lng)
        return render_template("result.html", location=location, service_provider=service_provider, lat=lat, lng=lng)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
