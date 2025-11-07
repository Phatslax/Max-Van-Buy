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

        # Price
        vat_match = re.search(r'£([\d,]+).*?(inc VAT|including VAT)', page, re.IGNORECASE)
        price_match = re.search(r'£([\d,]+)', page)
        no_vat_text = re.search(r'no VAT payable|ex VAT', page, re.IGNORECASE)

        if vat_match:
            price = int(vat_match.group(1).replace(",", ""))
        elif no_vat_text and price_match:
            price = int(price_match.group(1).replace(",", ""))
        elif price_match:
            price = int(price_match.group(1).replace(",", ""))
        else:
            price = None

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

            # Build depreciation curve independent of advert
            curve_years = sorted(base_curve.keys())
            curve_values = []
            for y in curve_years:
                val = base_curve[y]
                mileage_factor = annual_mileage / 15000
                adjusted_val = val / mileage_factor
                curve_values.append(adjusted_val)

            # Calculated market value (latest year)
            calc_value = curve_values[-1]

            # Adjust for write-off
            cat_discount = 0
            if repair_status.startswith("Cat N"):
                cat_discount = 0.15
            elif repair_status.startswith("Cat S"):
                cat_discount = 0.25
            calc_value *= (1 - cat_discount)

            # Price rating
            deviation_pct = (price - calc_value) / calc_value * 100
            if deviation_pct < -5:
                price_rating = "Good"
            elif deviation_pct > 5:
                price_rating = "Poor"
            else:
                price_rating = "Fair"

            # Depreciation after purchase year
            monthly_dep = (original_price - price) / (age_years * 12)
            yearly_dep = (original_price - price) / age_years

            # Plot curve and advert price dot
            plt.figure(figsize=(7, 4))
            plt.plot(curve_years, curve_values, label="Calculated Market Value Curve", linewidth=2)
            plt.scatter(current_year, price, color="red", zorder=5, label="Advert Price")
            plt.xlabel("Year")
            plt.ylabel("Value (£)")
            plt.title("Van Depreciation Curve")
            plt.legend()
            chart_buf = io.BytesIO()
            plt.savefig(chart_buf, format="png")
            plt.close()

            # Display summary
            st.subheader("📊 Summary")
            st.write(f"**Advert Price:** £{price:,.0f}")
            st.write(f"**Calculated Market Value:** £{calc_value:,.0f}")
            st.write(f"**Registration Year:** {year}")
            st.write(f"**Mileage:** {mileage:,} miles")
            st.write(f"**Write-off status:** {repair_status}")
            st.write(f"**How good is the price?** {deviation_pct:+.1f}% ({price_rating})")
            st.write(f"**Depreciation after purchase year:** £{monthly_dep:,.0f}/month, £{yearly_dep:,.0f}/year")
            st.image(chart_buf, caption="Calculated Market Value Curve with Advert Price", use_container_width=True)
