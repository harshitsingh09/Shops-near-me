import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Nearby Shops Finder", layout="centered")
st.title("🛍️ Nearby Shops Finder (OpenStreetMap + Overpass API)")

# User input
place = st.text_input("Enter a location (e.g., Bangalore, India)", "Bangalore, India")
radius = st.slider("Search radius (meters)", min_value=100, max_value=5000, value=1000)

def geocode_location(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': place_name,
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': 'streamlit-app'}
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    if results:
        return float(results[0]['lat']), float(results[0]['lon'])
    return None, None

def get_nearby_shops(lat, lon, radius=1000):
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["shop"](around:{radius},{lat},{lon});
      way["shop"](around:{radius},{lat},{lon});
      relation["shop"](around:{radius},{lat},{lon});
    );
    out center;
    """
    response = requests.post(overpass_url, data=query)
    return response.json()

if st.button("Find Nearby Shops"):
    with st.spinner("Locating and searching..."):
        lat, lon = geocode_location(place)
        if lat is None:
            st.error("❌ Could not geocode the provided location.")
        else:
            data = get_nearby_shops(lat, lon, radius)
            elements = data.get("elements", [])

            if not elements:
                st.warning("No shops found nearby.")
            else:
                st.success(f"Found {len(elements)} shops near {place}")
                # Map coordinates
                map_data = pd.DataFrame([
                    {
                        'lat': el.get('lat') or el.get('center', {}).get('lat'),
                        'lon': el.get('lon') or el.get('center', {}).get('lon')
                    }
                    for el in elements if (el.get('lat') or el.get('center', {}).get('lat'))
                ])
                st.map(map_data)

                # Show shop list
                for el in elements:
                    tags = el.get('tags', {})
                    name = tags.get('name', 'Unnamed Shop')
                    shop_type = tags.get('shop', 'Unknown Type')
                    st.markdown(f"**{name}** — {shop_type}")

