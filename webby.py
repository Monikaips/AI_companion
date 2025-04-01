import streamlit as st
import wikipedia
import google.generativeai as genai
import urllib.parse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your Gemini API key securely from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

# Generate Google Maps Search link
def get_maps_link(place, city):
    query = urllib.parse.quote(f"{place} {city}")
    return f"https://www.google.com/maps/search/?api=1&query={query}"

# Get city description from Wikipedia
def get_city_description(city):
    try:
        summary = wikipedia.summary(city, sentences=3, auto_suggest=False)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            summary = wikipedia.summary(e.options[0], sentences=3, auto_suggest=False)
            return summary
        except Exception as e:
            return "Sorry, couldn't find a proper description for this city."
    except Exception as e:
        return f"Sorry, couldn't fetch the description: {str(e)}"

# Get travel info from Gemini
def get_travel_info_gemini(city):
    prompt = f"""
    Provide concise travel details for {city} including:
    1. Famous places to visit
    2. Local foods
    3. Well-known malls
    4. Recommended restaurants
    Only give names in bullet points, no extra description.
    """
    try:
        model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error getting info from Gemini: {e}"

# Streamlit App UI
st.set_page_config(page_title="Destina -- AI Travel Chat App", page_icon="🌍")  # Set app page title and icon
st.title("  🎀 𝒟𝐸𝒮𝒯𝐼𝒩𝒜 🎀  -- AI Travel App")

# Initialize session state if not already initialized
if 'city_input' not in st.session_state:
    st.session_state.city_input = ''

# Sidebar for city input
with st.sidebar:
    st.header("City Information")
    city = st.text_input("Enter City Name", value=st.session_state.city_input, placeholder="e.g., Paris", key="city_input")

# Main content area
st.write("Enter any city to get travel insights and maps!")

# When the user presses Enter (i.e., when the city is provided)
if city:
    # Show loading spinner
    with st.spinner('Fetching travel details...'):
        # Get city description
        st.subheader(f"📍 About {city.title()}")
        city_description = get_city_description(city)
        st.write(city_description)

        # Get travel info from Gemini
        travel_info = get_travel_info_gemini(city)
        if "Error" in travel_info:
            st.error(f"❗ {travel_info}")
        else:
            # Parse and display the travel info
            lines = [line.strip('-• ').strip() for line in travel_info.split('\n') if line.strip()]
            
            # Categorize the travel info
            famous_places = []
            foods = []
            malls = []
            restaurants = []
            current_section = None

            for line in lines:
                if 'famous places' in line.lower():
                    current_section = famous_places
                elif 'local foods' in line.lower():
                    current_section = foods
                elif 'best malls' in line.lower():
                    current_section = malls
                elif 'recommended restaurants' in line.lower():
                    current_section = restaurants
                elif current_section is not None:
                    current_section.append(line)

            # Function to display each section of information in an expander (separate block)
            def display_section(title, items, icon):
                if items:
                    with st.expander(f"{icon} {title}", expanded=False):  # Creates a collapsible block
                        for item in items:  # Display all items
                            link = get_maps_link(item, city)
                            st.markdown(f"- {item} [📍 Google Maps]({link})")

            # Display each section inside an expander block
            display_section("Famous Places", famous_places, "🏛️")
            display_section("Popular Local Foods", foods, "🍽️")
            display_section("Best Malls", malls, "🛍️")
            display_section("Recommended Restaurants", restaurants, "🍴")

        # Provide Google Maps link for the city
        with st.expander("Explore the city", expanded=False):  # City link in an expander
            st.markdown(f"🌐 [Explore {city.title()} on Google Maps]({get_maps_link(city, '')})")

else:
    if city == "":
        st.warning("Please enter a valid city name.")
