import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# ——— 2025 Tax configuration constants ———
TAX_BRACKETS = {
    'income': [
        (0, 11925), (11925, 48475), (48475, 103350),
        (103350, 197300), (197300, 250525), (250525, 626350),
        (626350, float('inf'))
    ],
    'fica': [(0, 160000)],
    'capital_gains': [(0, 40000), (40001, 441450), (441451, float('inf'))]
}
TAX_RATES = {'income': [0.10,0.12,0.22,0.24,0.32,0.35,0.37],'fica': [0.0765],'capital_gains': [0.0,0.15,0.20]}
DEDUCTIONS = {'income': 15000, 'fica': 0, 'capital_gains': 0}

def calculate_tax(income, tax_type):
    brackets, rates, deduction = TAX_BRACKETS[tax_type], TAX_RATES[tax_type], DEDUCTIONS[tax_type]
    tax, taxable = 0, max(0, income - deduction)
    for (min_i, max_i), rate in zip(brackets, rates):
        if taxable > min_i:
            tax += (min(taxable, max_i) - min_i) * rate
        else:
            break
    return tax

def income_tax(i): return calculate_tax(i, 'income')
def fica_tax(i): return calculate_tax(i, 'fica')
def capital_gains_tax(i): return calculate_tax(i, 'capital_gains')

# Page configuration
st.set_page_config(page_title="Retirement Planning", layout="wide")

# Title
st.title("🌿 Retirement Planning Calculator")

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
end_salary = st.sidebar.number_input("End-of-Career Salary ($)", 0, 1_000_000, 100000, 1000)

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
    fixed_expenses = st.sidebar.number_input(
        "Fixed Annual Expenses ($)", 0, 1_000_000, 30000, 1000
    )
    savings_rate = None

current_savings = st.sidebar.number_input(
    "Current Investments ($, negative for debt)", -1_000_000, 100_000_000, 0, 1000
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

# Projection period
years = max(1, goal_retirement_age - age)

# Build DataFrame
df = pd.DataFrame({'Year': range(1, years+1)})
df['Age'] = age + df['Year'] - 1

# Salary Projection via geometric mean
growth = (end_salary/initial_salary)**(1/(years-1)) - 1 if initial_salary>0 and years>1 else 0
df['Salary'] = initial_salary * (1+growth)**(df['Year']-1)

# Tax calculations
df['Income Tax'] = df['Salary'].apply(income_tax)
df['FICA Tax']   = df['Salary'].apply(fica_tax)
df['Total Tax']  = df['Income Tax'] + df['FICA Tax']
df['After-Tax Income'] = df['Salary'] - df['Total Tax']

# Contribution and Spending
def compute_contrib_and_spend(row):
    ati = row['After-Tax Income']
    if mode == "Savings Rate":
        contrib = ati * savings_rate
        spend = ati - contrib
    else:
        spend = fixed_expenses
        contrib = max(0, ati - fixed_expenses)
    return pd.Series({'Contribution': contrib, 'Spending': spend})

df[['Contribution', 'Spending']] = df.apply(compute_contrib_and_spend, axis=1)

# Net Worth
df['Net Worth'] = 0
df.loc[0, 'Net Worth'] = current_savings + df.loc[0, 'Contribution']
for i in range(1, len(df)):
    prev = df.loc[i-1, 'Net Worth']
    contrib = df.loc[i, 'Contribution']
    r = rate_of_return if prev >= 0 else -interest_on_debt
    df.loc[i, 'Net Worth'] = prev * (1 + r) + contrib

# Investment Income and freedom
df['Investment Income'] = df['Net Worth'] * withdrawal_rate + other_income
df['Freedom'] = df['Investment Income'] >= df['Spending']
ff = df[df['Freedom']]
ff_age = int(ff.iloc[0]['Age']) if not ff.empty else None

# Results Overview
st.header("📊 Results Overview")
if ff_age:
    st.success(f"🎉 You can achieve financial freedom at age **{ff_age}**!")
else:
    st.warning("Financial freedom not reached by goal retirement age.")

# Color Palette
colors = {
    'net_worth': '#2E8B57', 'salary': '#66CDAA',
    'spending': '#8FBC8F', 'invest_income': '#3CB371'
}

# Net Worth Plot
fig1, ax1 = plt.subplots()
ax1.plot(df['Age'], df['Net Worth'], color=colors['net_worth'], label='Net Worth')
ax1.fill_between(df['Age'], 0, df['Net Worth'], color=colors['net_worth'], alpha=0.2)
ax1.set_xlabel('Age')
ax1.set_ylabel('Net Worth ($)')
ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'${int(x):,}'))
st.pyplot(fig1)

# Income vs Expenses Plot
fig2, ax2 = plt.subplots()
ax2.plot(df['Age'], df['Salary'], label='Salary', color=colors['salary'])
ax2.plot(df['Age'], df['Spending'], label='Spending', color=colors['spending'])
ax2.plot(df['Age'], df['Investment Income'], label='Investment Income', color=colors['invest_income'])
if ff_age: ax2.axvline(ff_age, linestyle='--', color='#006400', label='Freedom Age')
ax2.set_xlabel('Age')
ax2.set_ylabel('Amount ($)')
ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'${int(x):,}'))
ax2.legend()
st.pyplot(fig2)

# Detailed Projections
df_display = df.set_index('Age')[['Salary','After-Tax Income','Spending','Contribution','Net Worth','Investment Income']]
st.subheader("Detailed Financial Projections")
st.dataframe(df_display.style.format('${:,.0f}'))

# Additional Insights
totals = {
    'After-Tax Earnings': df['After-Tax Income'].sum(),
    'Taxes Paid': df['Total Tax'].sum(),
    'Total Savings': df['Contribution'].sum(),
    'Total Spending': df['Spending'].sum()
}
col1, col2 = st.columns(2)
col1.metric("Total After-Tax Earnings", f"${totals['After-Tax Earnings']:,}")
col1.metric("Total Taxes Paid", f"${totals['Taxes Paid']:,}")
col2.metric("Total Savings", f"${totals['Total Savings']:,}")
col2.metric("Total Spending", f"${totals['Total Spending']:,}")
