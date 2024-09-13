import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# Tax configuration constants
TAX_BRACKETS = {
    'income': [(0, 11000), (11001, 44725), (44726, 95375), (95376, 182100), (182101, 231250), (231251, 578125), (578126, float('inf'))],
    'fica': [(0, 160000)],
    'capital_gains': [(0, 40000), (40001, 441450), (441451, float('inf'))]
}

TAX_RATES = {
    'income': [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37],
    'fica': [0.0765],
    'capital_gains': [0.0, 0.15, 0.20]
}

DEDUCTIONS = {
    'income': 13850,
    'fica': 0,
    'capital_gains': 0
}

def calculate_tax(income, tax_type):
    brackets = TAX_BRACKETS[tax_type]
    rates = TAX_RATES[tax_type]
    deduction = DEDUCTIONS[tax_type]
    
    tax = 0
    taxable_income = max(0, income - deduction)
    
    for i in range(len(brackets)):
        min_income, max_income = brackets[i]
        rate = rates[i]
        if taxable_income > min_income:
            income_in_bracket = min(taxable_income, max_income) - min_income
            tax += income_in_bracket * rate
        else:
            break
    return tax

def income_tax(income):
    return calculate_tax(income, 'income')

def fica_tax(income):
    return calculate_tax(income, 'fica')

def capital_gains_tax(income):
    return calculate_tax(income, 'capital_gains')

# Streamlit app title
st.title("🌟 Retirement Planning Calculator")

# Sidebar for input parameters
st.sidebar.title("Input Parameters")

# Basic Information
st.sidebar.header("🧑 Personal Details")
age = st.sidebar.number_input("Current Age", min_value=14, max_value=100, value=30)
life_expectancy = st.sidebar.number_input("Life Expectancy", min_value=age+1, max_value=120, value=79)

st.sidebar.header("💼 Career Details")
initial_salary = st.sidebar.number_input("Initial Annual Salary ($)", min_value=0, max_value=1_000_000, value=52_000, step=1_000)
salary_growth = st.sidebar.slider("Expected Annual Salary Growth Rate (%)", min_value=0.0, max_value=20.0, value=3.0, step=0.1) / 100
diminish_growth = st.sidebar.checkbox("Diminish Salary Growth to Zero Over Career")

# Financial Information
st.sidebar.header("💰 Financial Details")
savings_rate = st.sidebar.slider("Savings Rate (% of After-Tax Income)", min_value=0, max_value=100, value=20) / 100
current_savings = st.sidebar.number_input("Current Investments ($)", min_value=-1_000_000, max_value=100_000_000, value=0, step=1_000)
interest_on_debt = st.sidebar.number_input("Interest Rate on Debt (%)", min_value=0.0, max_value=100.0, value=8.0, step=0.1) / 100

# Investment Assumptions
st.sidebar.header("📈 Investment Assumptions")
rate_of_return = st.sidebar.slider("Expected Annual Real Rate of Return (%)", min_value=0.0, max_value=15.0, value=7.0, step=0.1) / 100
withdrawal_rate = st.sidebar.slider("Withdrawal Rate During Retirement (%)", min_value=0.0, max_value=10.0, value=4.0, step=0.1) / 100
other_income = st.sidebar.number_input("Other Retirement Income ($)", min_value=0, max_value=1_000_000, value=0, step=1_000)

# Data Calculation
career_length = life_expectancy - age
df = pd.DataFrame({'Year': range(1, career_length + 1)})
df['Age'] = df['Year'] + age - 1

# Salary Projection
if diminish_growth:
    total_years = career_length
    df['Salary'] = initial_salary * (1 + salary_growth * (1 - (df['Year'] - 1) / total_years))
else:
    df['Salary'] = initial_salary * ((1 + salary_growth) ** (df['Year'] - 1))

# Tax Calculations
df['Income Tax'] = df['Salary'].apply(income_tax)
df['FICA Tax'] = df['Salary'].apply(fica_tax)
df['Total Tax'] = df['Income Tax'] + df['FICA Tax']
df['After-Tax Income'] = df['Salary'] - df['Total Tax']

# Savings and Net Worth
df['Retirement Contribution'] = df['After-Tax Income'] * savings_rate
df['Net Worth'] = 0
df.loc[0, 'Net Worth'] = current_savings + df.loc[0, 'Retirement Contribution']

for i in range(1, len(df)):
    previous_net_worth = df.loc[i - 1, 'Net Worth']
    contribution = df.loc[i, 'Retirement Contribution']
    growth_rate = rate_of_return if previous_net_worth >= 0 else -interest_on_debt
    df.loc[i, 'Net Worth'] = previous_net_worth * (1 + growth_rate) + contribution

df['Spending'] = df['After-Tax Income'] - df['Retirement Contribution']
df['Investment Income'] = df['Net Worth'] * withdrawal_rate + other_income

# Determine Financial Freedom Age
difference = df['Investment Income'] - df['Spending']
df['Financial Freedom'] = difference >= 0
first_ff_age = df[df['Financial Freedom']].iloc[0]['Age'] if df['Financial Freedom'].any() else None

# Display Results
st.header("📊 Results Overview")

if first_ff_age:
    st.success(f"🎉 You can achieve financial freedom at age **{int(first_ff_age)}**!")
else:
    st.warning("Based on your current inputs, financial freedom is not achieved before life expectancy.")

# Plotting
st.subheader("Net Worth Over Time")
fig1, ax1 = plt.subplots()
ax1.plot(df['Age'], df['Net Worth'], label='Net Worth', color='green')
ax1.fill_between(df['Age'], 0, df['Net Worth'], color='green', alpha=0.1)
ax1.set_xlabel('Age')
ax1.set_ylabel('Net Worth ($)')
ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'${int(x):,}'))
st.pyplot(fig1)

st.subheader("Income and Expenses Over Time")
fig2, ax2 = plt.subplots()
ax2.plot(df['Age'], df['Salary'], label='Salary', color='blue')
ax2.plot(df['Age'], df['Spending'], label='Spending', color='orange')
ax2.plot(df['Age'], df['Investment Income'], label='Investment Income', color='green')
if first_ff_age:
    ax2.axvline(x=first_ff_age, color='red', linestyle='--', label='Financial Freedom Age')
ax2.set_xlabel('Age')
ax2.set_ylabel('Amount ($)')
ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'${int(x):,}'))
ax2.legend()
st.pyplot(fig2)

# Detailed Data Table
st.subheader("Detailed Financial Projections")
st.dataframe(df[['Age', 'Salary', 'After-Tax Income', 'Spending', 'Retirement Contribution', 'Net Worth', 'Investment Income']].style.format('${:,.0f}'))

# Additional Insights
st.header("📈 Additional Insights")
total_earnings = df['After-Tax Income'].sum()
total_taxes = df['Total Tax'].sum()
total_savings = df['Retirement Contribution'].sum()
total_spending = df['Spending'].sum()

col1, col2 = st.columns(2)
col1.metric("Total After-Tax Earnings", f"${total_earnings:,.0f}")
col1.metric("Total Taxes Paid", f"${total_taxes:,.0f}")
col2.metric("Total Savings", f"${total_savings:,.0f}")
col2.metric("Total Spending", f"${total_spending:,.0f}")
