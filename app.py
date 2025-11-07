import streamlit as st
import datetime, re, requests, io
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

# --- Depreciation Curves (Average vs High Use) ---
avg_curve = {
    2018: 30000, 2019: 24000, 2020: 18000, 2021: 16000,
    2022: 14000, 2023: 12500, 2024: 11000, 2025: 12000,
    2026: 11400, 2027: 10830, 2028: 10289, 2029: 9775, 2030: 9286
}

highuse_curve = {
    2018: 30000, 2019: 24000, 2020: 18000, 2021: 16000,
    2022: 14000, 2023: 12500, 2024: 11000, 2025: 9500,
    2026: 8740, 2027: 8040, 2028: 7396, 2029: 6805, 2030: 6260
}

st.set_page_config(page_title="Ford Transit Custom Depreciation Tool", page_icon="🚐", layout="centered")
st.title("🚐 Ford Transit Custom Depreciation Tool (UK)")
st.caption("Analyse advert prices, compare to expected depreciation, and export a professional PDF report.")

url = st.text_input("Paste advert URL (AutoTrader, eBay, etc.)")

col1, col2, col3 = st.columns(3)
year = col1.number_input("Registration Year", min_value=2010, max_value=2025, value=2018)
mileage = col2.number_input("Mileage", min_value=0, value=60000, step=1000)
price = col3.number_input("Advert Price (£)", min_value=0, value=12000, step=500)

# Add repair status dropdown
repair_status = st.selectbox(
    "Insurance Write-off Category (if applicable)",
    ["None", "Cat N (Non-structural)", "Cat S (Structural)"]
)

def extract_data(url):
    """Extracts year, price, and mileage from advert HTML using simple regex."""
    try:
        page = requests.get(url, timeout=5).text
        year_match = re.search(r'\b(20\d{2})\b', page)
        price_match = re.search(r'£([\d,]+)', page)
        mileage_match = re.search(r'([\d,]+)\s*miles', page, re.IGNORECASE)
        return {
            "year": int(year_match.group(1)) if year_match else None,
            "price": int(price_match.group(1).replace(",", "")) if price_match else None,
            "mileage": int(mileage_match.group(1).replace(",", "")) if mileage_match else None,
        }
    except Exception:
        return {}

if url:
    parsed = extract_data(url)
    if parsed.get("year"): year = parsed["year"]
    if parsed.get("price"): price = parsed["price"]
    if parsed.get("mileage"): mileage = parsed["mileage"]

if st.button("Generate Depreciation Report"):
    current_year = datetime.date.today().year
    age = current_year - year
    original_price = avg_curve[2018]

    expected_value = avg_curve.get(current_year, list(avg_curve.values())[-1])
    expected_adjusted = expected_value - max(0, (mileage - 60000) * 0.05)

    # Apply category-based reduction
    cat_discount = 0
    if repair_status.startswith("Cat N"):
        cat_discount = 0.15
    elif repair_status.startswith("Cat S"):
        cat_discount = 0.25

    expected_adjusted *= (1 - cat_discount)

    deviation_pct = (price - expected_adjusted) / expected_adjusted * 100

    if deviation_pct <= -10:
        rating = "🟢 Low"
    elif deviation_pct >= 10:
        rating = "🔴 High"
    else:
        rating = "🟡 Fair"

    monthly_dep = (original_price - price) / (age * 12)

    years = list(avg_curve.keys())
    avg_values = list(avg_curve.values())
    high_values = list(highuse_curve.values())

    plt.figure(figsize=(7, 4))
    plt.plot(years, avg_values, label="Average-Use Curve", linewidth=2)
    plt.plot(years, high_values, linestyle="--", label="High-Use Curve", linewidth=2)
    plt.scatter([year], [price], color="red", label="Advert Price", zorder=5)
    plt.xlabel("Year")
    plt.ylabel("Value (£)")
    plt.title("Depreciation Curves for Ford Transit Custom")
    plt.legend()

    chart_buf = io.BytesIO()
    plt.savefig(chart_buf, format="png")
    plt.close()

    st.subheader("📊 Summary")
    st.write(f"**Advert year:** {year}")
    st.write(f"**Advert price:** £{price:,.0f}")
    st.write(f"**Mileage:** {mileage:,} miles")
    st.write(f"**Repair status:** {repair_status}")
    st.write(f"**Expected value (adjusted):** £{expected_adjusted:,.0f}")
    st.write(f"**Deviation from expected:** {deviation_pct:+.1f}% ({rating})")
    st.write(f"**Average monthly depreciation:** £{monthly_dep:,.0f}/month")

    st.image(chart_buf, caption="Depreciation comparison (Average vs High use)", use_container_width=True)

    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>Ford Transit Custom Depreciation Report</b>", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Advert URL: <a href='{url}'>{url}</a>", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Registration Year:</b> {year}", styles['Normal']))
    story.append(Paragraph(f"<b>Mileage:</b> {mileage:,} miles", styles['Normal']))
    story.append(Paragraph(f"<b>Repair Status:</b> {repair_status}", styles['Normal']))
    story.append(Paragraph(f"<b>Advert Price:</b> £{price:,.0f}", styles['Normal']))
    story.append(Paragraph(f"<b>Expected Value (adjusted):</b> £{expected_adjusted:,.0f}", styles['Normal']))
    story.append(Paragraph(f"<b>Deviation from Expected:</b> {deviation_pct:+.1f}% ({rating})", styles['Normal']))
    story.append(Paragraph(f"<b>Average Monthly Depreciation:</b> £{monthly_dep:,.0f}/month", styles['Normal']))
    story.append(Spacer(1, 12))

    chart_buf.seek(0)
    story.append(Image(chart_buf, width=6*inch, height=3*inch))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Blue line = Average use | Dashed line = High use | Red dot = Advert", styles['Italic']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Generated on {datetime.date.today().strftime('%d %B %Y')}", styles['Italic']))

    doc.build(story)
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_buffer.getvalue(),
        file_name=f"Transit_Custom_Report_{year}.pdf",
        mime="application/pdf"
    )
