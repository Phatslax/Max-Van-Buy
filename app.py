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
annual_mileage =_
