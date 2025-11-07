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

st.set_page_config(page_title="Van Value Assessment Tool", page_icon="🚐", layout="centered")
st.title("🚐 Van Value Assessment Tool (UK)")
st.caption("Analyse advert prices and compare to calculated market value.")

# Inputs
url = st.text_input("Paste advert URL (AutoTrader, eBay, etc.)")
annual_mileage = st.number_input(
    "Estimated Annual Mileage (miles/year)",
    min_value=5000, max_value=50000, value=15000, step=1000
)

def extract_data(url):
    try:
        page = requests.get(url, timeout=5).text

        # Year
        year_match = re.search(r'\b(20\d{2})\b', page)
        year = int(year_match.group(1)) if year_match else None

        # Price (VAT priority)
        vat_match = re.search(r'£([\d,]+).*?(inc VAT|including VAT)', page, re.IGNORECASE)
        price_match = re.search(r'£([\d,]+)', page)
        no_vat_text = re.search(r'no VAT payable|ex VAT', page, re.IGNORECASE)

        if vat_match:
            price = int(vat_match.group(1).replace(",", ""))
        elif no_vat_text:
            price = int(price_match.group(1).replace(",", "")) if price_match else None
        else:
            price = int(price_match.group(1).replace(",", "")) if price_match else None

        # Mileage
        mileage_match = re.search(r'([\d,]+)\s*miles', page, re.IGNORECASE)
        mileage = int(mileage_match.group(1).replace(",", "")) if mileage_match else None

        # Write-off
        repair_status = "None"
        if re.search(r'Cat S', page, re.IGNORECASE):
            repair_status = "Cat S (Structural)"
        elif re.search(r'Cat N', page, re.IGNORECASE):
            repair_status = "Cat N (Non-structural)"

        return {"year": year, "price": price, "mileage": mileage, "repair_status": repair_status}
    except Exception:
        return {}

if st.button("Generate Van Assessment"):
    if not url:
        st.warning("Please paste a valid advert URL.")
    else:
        data = extract_data(url)
        year = data.get("year")
        price = data.get("price")
        mileage = data.get("mileage")
        repair_status = data.get("repair_status")

        if not all([year, price, mileage]):
            st.error("Could not extract necessary data from the advert.")
        else:
            current_year = datetime.date.today().year
            age_years = current_year - year
            original_price = base_curve[2018]

            # Adjust depreciation curve
            curve_years = sorted(base_curve.keys())
            curve_values = []
            for y in curve_years:
                val = base_curve[y]
                mileage_factor = annual_mileage / 15000
                adjusted_val = val / mileage_factor
                curve_values.append(adjusted_val)

            # Calculated Market Value
            calc_value = curve_values[-1]

            # Write-off adjustment
            cat_discount = 0
            if repair_status.startswith("Cat N"):
                cat_discount = 0.15
            elif repair_status.startswith("Cat S"):
                cat_discount = 0.25
            calc_value *= (1 - cat_discount)

            # Price assessment
            deviation_pct = (price - calc_value) / calc_value * 100
            if deviation_pct < -5:
                price_rating = "Good"
            elif dev
