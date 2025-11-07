import streamlit as st
import datetime, re, requests, io
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

# Base depreciation curve (average condition)
base_curve = {
    2018: 30000, 2019: 24000, 2020: 18000, 2021: 16000,
    2022: 14000, 2023: 12500, 2024: 11000, 2025: 12000,
    2026: 11400, 2027: 10830, 2028: 10289, 2029: 9775, 2030: 9286
}

# Streamlit page configuration
st.set_page_config(page_title="Van Value Assessment Tool", page_icon="🚐", layout="centered")
st.title("🚐 Van Value Assessment Tool (UK)")
st.caption("Analyse advert prices and compare to calculated market value.")

# Inputs
url = st.text_input("Paste advert URL (AutoTrader, eBay, etc.)")
annual_mileage = st.number_input(
    "Estimated Annual Mileage (miles/year)", 
    min_value=5000, max_value=50000, value=15000, step=1000
)

# Function to extract advert data
def extract_data(url):
    try:
        page = requests.get(url, timeout=5).text

        # Extract registration year
        year_match = re.search(r'\b(20\d{2})\b', page)
        year = int(year_match.group(1)) if year_match else None

        # Extract price, prioritize VAT-inclusive
        vat_match = re.search(r'£([\d,]+).*?(inc VAT|including VAT)', page, re.IGNORECASE)
        price_match = re.search(r'£([\d,]+)', page)
        no_vat_text = re.search(r'no VAT payable|ex VAT', page, re.IGNORECASE)

        if vat_match:
            price = int(vat_match.group(1).replace(",", ""))
        elif no_vat_text:
            price = int(price_match.group(1).replace(",", "")) if price_match else None
        else:
            price = int(price_match.group(1).repl_
