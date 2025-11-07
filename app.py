# app.py - Van Value Assessment Tool
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from fpdf import FPDF

# -----------------------
# Helper Functions
# -----------------------

def calculate_historic_curve(reg_year, purchase_price, current_year, mileage_multiplier):
    years = list(range(reg_year, current_year + 1))
    # Typical depreciation percentages per year (example for panel vans)
    dep_percent = [0.25, 0.15, 0.10, 0.08, 0.07, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
    curve = []
    value = purchase_price
    for i, year in enumerate(years):
        if i < len(dep_percent):
            value = value * (1 - dep_percent[i])
        else:
            value = value * (1 - dep_percent[-1])
        curve.append(value * mileage_multiplier)
    return years, curve

def calculate_future_curve(current_value, years_ahead, annual_mileage, default_mileage=10000, dep_rate=0.07):
    years = list(range(years_ahead[0], years_ahead[-1]+1))
    curve = []
    value = current_value
    mileage_factor = annual_mileage / default_mileage
    for _ in years:
        adjusted_dep = dep_rate * mileage_factor
        value = value * (1 - adjusted_dep)
        curve.append(value)
    return years, curve

def price_rating(deviation_percent):
    if deviation_percent < -5:
        return f"Good ({deviation_percent:.1f}%)"
    elif deviation_percent > 5:
        return f"Poor (+{deviation_percent:.1f}%)"
    else:
        return f"Fair ({deviation_percent:.1f}%)"

def generate_pdf(advert_price, market_value, curve_years, curve_values, file_name="Van_Report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Van Value Assessment Report", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Advert Price: £{advert_price:,.0f}", ln=True)
    pdf.cell(0, 10, f"Calculated Market Value: £{market_value:,.0f}", ln=True)
    pdf.ln(10)
    # Save chart
    plt.figure(figsize=(6,3))
    plt.plot(curve_years, curve_values, marker='o', label='Depreciation Curve')
    plt.xlabel("Year")
    plt.ylabel("Value (£)")
    plt.title("Van Depreciation")
    plt.grid(True)
    plt.tight_layout()
    chart_file = "/tmp/depreciation_chart.png"
    plt.savefig(chart_file)
    plt.close()
    pdf.image(chart_file, x=10, y=60, w=190)
    pdf.output(file_name)
    return file_name

# -----------------------
# Streamlit UI
# -----------------------

st.title("Van Value Assessment Tool")

st.markdown("Paste the van advert info and provide annual mileage.")

# User Inputs
reg_year = st.number_input("Registration Year", min_value=2000, max_value=2030, value=2018, step=1)
purchase_price = st.number_input("Original New Purchase Price (£)", min_value=5000, value=30000, step=500)
advert_price = st.number_input("Advert Price (£)", min_value=1000, value=15000, step=100)
advert_mileage = st.number_input("Advert Mileage (mi)", min_value=0, value=50000, step=1000)
annual_mileage = st.number_input("Projected Annual Mileage (mi)", min_value=1000, value=10000, step=1000)

current_year = 2025  # You can make dynamic via datetime.datetime.now().year
mileage_multiplier = 1.0  # can be adjusted from market-based data
mileage_multiplier = 1 + (10000 - advert_mileage)/100000  # simple example adjustment

# Historic curve
hist_years, hist_values = calculate_historic_curve(reg_year, purchase_price, current_year, mileage_multiplier)

# Future curve projection
future_years, future_values = calculate_future_curve(hist_values[-1], list(range(current_year+1,2031)), annual_mileage)

# Combine for plotting
all_years = hist_years + future_years
all_values = hist_values + future_values

# Plot
fig, ax = plt.subplots()
ax.plot(all_years, all_values, label='Depreciation Curve')
ax.scatter([current_year], [advert_price], color='red', label='Advert Price')
ax.set_xlabel("Year")
ax.set_ylabel("Value (£)")
ax.set_title("Van Depreciation")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Deviation
deviation = (advert_price - hist_values[-1]) / hist_values[-1] * 100
st.write(f"How good is the price? {price_rating(deviation)}")
st.write(f"Calculated Market Value Today: £{hist_values[-1]:,.0f}")
st.write(f"Depreciation per year since purchase: £{(purchase_price - hist_values[-1]) / (current_year - reg_year):,.0f}")
st.write(f"Depreciation per month since purchase: £{(purchase_price - hist_values[-1]) / ((current_year - reg_year)*12):,.0f}")

# Generate PDF
if st.button("Generate PDF Report"):
    file = generate_pdf(advert_price, hist_values[-1], all_years, all_values)
    st.success(f"PDF report generated: {file}")
