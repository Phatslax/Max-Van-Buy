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
    for i, year in enumerate(years):
        if i < len(dep_percent):
            value = value * (1 - dep_percent[i])
        else:
            value = value * (1 - dep_percent[-1])
        curve.append(value * mileage_multiplie_*
