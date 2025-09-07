# -*- coding: utf-8 -*-
"""
Created on Sun Jun  8 13:51:29 2025

@author: zekes
"""
import streamlit as st

# Sidebar Inputs
st.sidebar.title("Input Parameters")

# Personal Details
st.sidebar.header("🧑 Personal Details")
age = st.sidebar.number_input("Current Age", 14, 100, 30)
goal_retirement_age = st.sidebar.number_input(
    "Goal Retirement Age", age+1, 120, 67
)

# Career Details
st.sidebar.header("💼 Career Details")
initial_salary = st.sidebar.number_input("Current Salary ($)", 0, 1_000_000, 52000, 1000)
end_salary = st.sidebar.number_input("End-of-Career Salary ($)", 0, 1_000_000, 75000, 1000)

# Financial Details Mode Toggle
st.sidebar.header("💰 Financial Details")
mode = st.sidebar.radio(
    "Contribution Method", ["Savings Rate", "Fixed Expenses"], index=0
)
if mode == "Savings Rate":
    savings_rate = st.sidebar.slider(
        "Savings Rate (% of After-Tax Income)", 0, 100, 20
    ) / 100
    fixed_expenses = None
else:
    fixed_expenses = st.sidebar.slider(
        "Savings Rate (% of After-Tax Income)", 0, 100, 20
    ) / 100
    savings_rate = None

current_savings = st.sidebar.number_input(
    "Current Investments ($, negative for debt)", -1_000_000, 100_000_000, 36_000, 1000
)

# Advanced Settings
with st.sidebar.expander("Advanced Settings"):
    interest_on_debt = st.number_input(
        "Interest Rate on Debt (%)", 0.0, 100.0, 8.0, 0.1
    ) / 100
    st.header("📈 Investment Assumptions")
    rate_of_return = st.slider(
        "Real Rate of Return (%)", 0.0, 15.0, 7.0, 0.1
    ) / 100
    withdrawal_rate = st.slider(
        "Withdrawal Rate (%)", 0.0, 10.0, 4.0, 0.1
    ) / 100
    other_income = st.number_input(
        "Other Retirement Income ($)", 0, 1_000_000, 0, 1000
    )
