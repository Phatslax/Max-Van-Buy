# app.py - Van Value Assessment Tool
import streamlit as st
import matplotlib.pyplot as plt
import datetime

# -----------------------
# Helper Functions
# -----------------------

def calculate_historic_curve(reg_year, purchase_price, current_year, mileage_multiplier):
    years = list(range(reg_year, current_year + 1))
    dep_percent = [0.25, 0.15, 0.10, 0.08, 0.07, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
    curve = []
    value = purchase_price
    for i in range(len(years)):
        rate = dep_percent[i] if i < len(dep_percent) else dep_percent[-1]
        value = value * (1 - rate)
        curve.append(value * mileage_multiplier)
    return years, curve

def calculate_future_curve(current_value, start_year, end_year, annual_mileage, default_mileage=10000, dep_rate=0.07):
    years = list(range(start_year, end_year + 1))
    curve = []
    value = current_value
    mileage_factor = float(annual_mileage) / float(default_mileage)
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

# -----------------------
# Streamlit UI
# -----------------------

st.title("Van Value Assessment Tool")
st.markdown("Enter the van details and projected annual mileage:")

# User Inputs
reg_year = int(st.number_input("Registration Year", min_value=2000, max_value=2030, value=2018, step=1))
purchase_price = float(st.number_input("Original New Purchase Price (£)", min_value=5000, value=30000, step=500))
advert_price = float(st.number_input("Advert Price (£)", min_value=1000, value=15000, step=100))
advert_mileage = float(st.number_input("Advert Mileage (mi)", min_value=0, value=50000, step=1000))
annual_mileage = float(st.number_input("Projected Annual Mileage (mi)", min_value=1000, value=10000, step=1000))

# Current year
current_year = datetime.datetime.now().year

# Mileage adjustment
mileage_multiplier = 1 + (10000 - advert_mileage) / 100000

# Historic curve
hist_years, hist_values = calculate_historic_curve(reg_year, purchase_price, current_year, mileage_multiplier)

# Future curve
future_start_year = current_year + 1
future_end_year = 2030
future_years, future_values = calculate_future_curve(hist_values[-1], future_start_year, future_end_year, annual_mileage)

# Combine for plotting
all_years = hist_years + future_years
all_values = hist_values + future_values

# Plot
fig, ax = plt.subplots()
ax.plot(all_years, all_values, label='Depreciation Curve', color='blue')
ax.scatter([current_year], [advert_price], color='red', label='Advert Price')
ax.set_xlabel("Year")
ax.set_ylabel("Value (£)")
ax.set_title("Van Depreciation")
ax.grid(True)
ax.legend()
st.pyplot(fig, clear_figure=True)

# Deviation
deviation = (advert_price - hist_values[-1]) / hist_values[-1] * 100
st.write(f"How good is the price? {price_rating(deviation)}")
st.write(f"Calculated Market Value Today: £{hist_values[-1]:,.0f}")
years_owned = current_year - reg_year
if years_owned > 0:
    per_year_dep = (purchase_price - hist_values[-1]) / years_owned
    per_month_dep = per_year_dep / 12
else:
    per_year_dep = 0
    per_month_dep = 0
st.write(f"Depreciation per year since purchase: £{per_year_dep:,.0f}")
st.write(f"Depreciation per month since purchase: £{per_month_dep:,.0f}")
