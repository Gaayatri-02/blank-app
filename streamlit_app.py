import streamlit as st
import random
from datetime import datetime, timedelta
import folium 
from streamlit_folium import folium_static
import requests 
import pandas as pd

import plotly.express as px 
import json
import re
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'tracking_numbers' not in st.session_state:
    # Enhanced tracking data with GPS coordinates and weather data
    st.session_state.tracking_numbers = {
        'TRK123456': {
            'status': 'In Transit',
            'origin': {'city': 'New York', 'coords': [40.7128, -74.0060]},
            'destination': {'city': 'Los Angeles', 'coords': [34.0522, -118.2437]},
            'current_location': {'city': 'Chicago', 'coords': [41.8781, -87.6298]},
            'estimated_delivery': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'route_points': [
                [40.7128, -74.0060],  # New York
                [41.8781, -87.6298],  # Chicago
                [39.7392, -104.9903],  # Denver
                [34.0522, -118.2437]   # Los Angeles
            ],
            'updates': [
                {
                    'timestamp': '2024-10-28 10:00',
                    'location': 'New York',
                    'status': 'Package Picked Up',
                    'temperature': 72,
                    'weather': 'Clear'
                },
                {
                    'timestamp': '2024-10-28 15:30',
                    'location': 'Chicago',
                    'status': 'In Transit',
                    'temperature': 68,
                    'weather': 'Cloudy'
                }
            ],
            'package_details': {
                'weight': '5.2 kg',
                'dimensions': '30x20x15 cm',
                'type': 'Priority',
                'handling': 'Fragile'
            },
            'carbon_footprint': 245.5,  # CO2 emissions in kg
            'delivery_preferences': {
                'signature_required': True,
                'safe_place': 'Front Porch',
                'notifications': ['email', 'sms']
            }
        }
    }

def calculate_delivery_analytics(tracking_number):
    """Calculate delivery performance analytics"""
    package = st.session_state.tracking_numbers.get(tracking_number)
    if not package:
        return None

    analytics = {
        'distance_covered': random.uniform(800, 1200),  # miles
        'time_in_transit': random.uniform(24, 72),      # hours
        'stops_made': len(package['updates']),
        'efficiency_score': random.uniform(85, 98),     # percentage
        'estimated_fuel_usage': random.uniform(10, 30)  # gallons
    }
    return analytics

def create_route_map(tracking_number):
    """Create an interactive map with the delivery route"""
    package = st.session_state.tracking_numbers.get(tracking_number)
    if not package:
        return None

    # Create map centered on current location
    m = folium.Map(
        location=package['current_location']['coords'],
        zoom_start=4
    )

    # Add markers for origin and destination
    folium.Marker(
        package['origin']['coords'],
        popup=f"Origin: {package['origin']['city']}",
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(m)

    folium.Marker(
        package['destination']['coords'],
        popup=f"Destination: {package['destination']['city']}",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # Add current location marker
    folium.Marker(
        package['current_location']['coords'],
        popup=f"Current Location: {package['current_location']['city']}",
        icon=folium.Icon(color='blue', icon='truck', prefix='fa')
    ).add_to(m)

    # Draw route line
    folium.PolyLine(
        package['route_points'],
        weight=2,
        color='blue',
        opacity=0.8
    ).add_to(m)

    return m

def create_delivery_timeline(tracking_number):
    """Create a visual timeline of delivery updates"""
    package = st.session_state.tracking_numbers.get(tracking_number)
    if not package:
        return None

    df = pd.DataFrame(package['updates'])
    fig = px.timeline(
        df,
        x_start='timestamp',
        y='location',
        color='status',
        title='Delivery Timeline'
    )
    return fig

def get_weather_alert(location, temperature):
    """Generate weather-based delivery alerts"""
    alerts = []
    if temperature > 85:
        alerts.append(f"⚠️ High temperature alert in {location}. Package may require special handling.")
    elif temperature < 32:
        alerts.append(f"❄️ Freezing conditions in {location}. Delay possible.")
    return alerts

def get_bot_response(user_input):
    """Enhanced bot response with additional features"""
    user_input = user_input.lower()

    # Track package with enhanced details
    if 'track' in user_input or 'status' in user_input:
        tracking_match = re.search(r'TRK\d{6}', user_input.upper())
        if tracking_match:
            tracking_number = tracking_match.group()
            if tracking_number in st.session_state.tracking_numbers:
                package = st.session_state.tracking_numbers[tracking_number]

                # Create map
                st.write("📍 Live Location Tracking")
                map_obj = create_route_map(tracking_number)
                if map_obj:
                    folium_static(map_obj)

                # Show timeline
                st.write("📅 Delivery Timeline")
                timeline = create_delivery_timeline(tracking_number)
                if timeline:
                    st.plotly_chart(timeline)

                # Show analytics
                analytics = calculate_delivery_analytics(tracking_number)
                if analytics:
                    st.write("📊 Delivery Analytics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Distance Covered", f"{analytics['distance_covered']:.1f} mi")
                    with col2:
                        st.metric("Time in Transit", f"{analytics['time_in_transit']:.1f} hrs")
                    with col3:
                        st.metric("Efficiency Score", f"{analytics['efficiency_score']:.1f}%")

                # Weather alerts
                current_weather = package['updates'][-1]
                alerts = get_weather_alert(current_weather['location'], current_weather['temperature'])
                if alerts:
                    for alert in alerts:
                        st.warning(alert)

                return f"""
                📦 Tracking Number: {tracking_number}
                Status: {package['status']}
                Origin: {package['origin']['city']}
                Destination: {package['destination']['city']}
                Estimated Delivery: {package['estimated_delivery']}
                Current Location: {package['current_location']['city']}

                Package Details:
                - Weight: {package['package_details']['weight']}
                - Dimensions: {package['package_details']['dimensions']}
                - Type: {package['package_details']['type']}

                🌱 Carbon Footprint: {package['carbon_footprint']} kg CO2

                Delivery Preferences:
                - Signature Required: {'Yes' if package['delivery_preferences']['signature_required'] else 'No'}
                - Safe Place: {package['delivery_preferences']['safe_place']}
                """
            else:
                return "Sorry, I couldn't find that tracking number in our system."
        else:
            return "Please provide a valid tracking number in the format TRK######"

    elif 'carbon' in user_input or 'environmental' in user_input:
        return "We calculate the carbon footprint of each delivery and offset it through our environmental programs. Would you like to see the environmental impact of a specific delivery?"

    elif 'weather' in user_input:
        return "I can provide real-time weather updates along your package's route. Please provide a tracking number."

    elif 'analytics' in user_input:
        return "I can show you detailed analytics including distance covered, time in transit, and efficiency scores. Please provide a tracking number."

    # Original response handlers
    elif any(word in user_input for word in ['hello', 'hi', 'hey']):
        return "Hello! How can I help you with your delivery today?"

    elif 'delivery time' in user_input:
        return "Standard delivery typically takes 2-5 business days. Express delivery is available for 1-2 business days."

    elif 'help' in user_input:
        return """
        I can help you with:
        - 📍 Real-time GPS tracking
        - 🌡️ Weather alerts along delivery route
        - 📊 Delivery analytics and performance metrics
        - 🌱 Carbon footprint tracking
        - 📱 Delivery preferences management
        - 📦 Package details and status updates

        What would you like to know more about?
        """

    else:
        return "I'm not sure I understand. Could you rephrase that or ask for 'help' to see what I can do?"
    


st.title("📦 Advanced Logistics Delivery Assistant")
st.write("Welcome to your AI logistics assistant with GPS tracking and advanced features!")

user_input = st.text_input("Type your message here:", key="user_input")

if st.button("Send"):
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        bot_response = get_bot_response(user_input)
        st.session_state.chat_history.append(("bot", bot_response))


for role, message in st.session_state.chat_history:
    if role == "user":
        st.write(f"You: {message}")
    else:
        st.write(f"🤖 Assistant: {message}")

# Enhanced sidebar with additional features
st.sidebar.header("📱 Quick Actions")
st.sidebar.write("Try these features:")

# Sample tracking numbers
st.sidebar.header("📦 Sample Tracking")


for tracking_num in st.session_state.tracking_numbers.keys():
    st.sidebar.code(tracking_num)

if st.sidebar.button("📍 Track Package"):
    st.session_state.chat_history.append(("bot", "Please enter a tracking number in the format TRK######"))

if st.sidebar.button("🌡️ Weather Alerts"):
    st.session_state.chat_history.append(("bot", "I'll check for weather conditions along your package's route. Please provide a tracking number."))

if st.sidebar.button("📊 View Analytics"):
    st.session_state.chat_history.append(("bot", "I can show you detailed delivery analytics. Please provide a tracking number."))

if st.sidebar.button("🌱 Carbon Footprint"):
    st.session_state.chat_history.append(("bot", "I can show you the environmental impact of your delivery. Please provide a tracking number."))

st.sidebar.header("⚙️ Settings")
notification_preference = st.sidebar.multiselect(
    "Notification Preferences",
    ["Email", "SMS", "Push Notifications"],
    default=["Email"]
)
# Clear chat button
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()