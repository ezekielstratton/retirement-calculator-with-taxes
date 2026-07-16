import streamlit as st
from calculations import build_financials
from visualization import render_visualizations

# ——— 1) Page setup & Inputs ———
st.set_page_config(page_title="Retirement Planning", layout="wide")
st.title("Retirement Planning Calculator")

# Personal Details
age = st.sidebar.number_input(
    "Current Age", 14, 100, 30,
    help="Your current age. This sets the starting point for the retirement projection."
)
goal_retirement_age = st.sidebar.number_input(
    "Goal Retirement Age", age+1, 120, 67,
    help="The age at which you plan to retire. This determines when income stops and withdrawals begin."
)

# Career Details
initial_salary = st.sidebar.number_input(
    "Current Salary ($)", 0, 1_000_000, 52_000, 1_000,
    help="Your current annual salary before taxes."
)
salary_growth_rate = st.sidebar.slider(
    "Yearly Salary Growth Rate (%)", 0.0, 20.0, 2.0, 0.5,
    help="Expected annual raise or salary growth rate."
) / 100

# Financial Details Mode Toggle
mode = st.sidebar.radio(
    "Contribution Method", ["Savings Rate", "Fixed Expenses"], index=0,
    help="Choose whether to estimate savings based on a fixed savings rate or fixed monthly expenses."
)
if mode == "Savings Rate":
    savings_rate = st.sidebar.slider(
        "Savings Rate (% of After-Tax Income)", 0, 100, 20,
        help="The portion of your after-tax income you save each year."
    ) / 100
    fixed_expenses = None
else:
    fixed_expenses = st.sidebar.number_input(
        "Yearly Expenses ($)", 1, 1_000_000, 40_000, 1_000,
        help="Your projected yearly spending. Savings will be calculated as income minus these expenses."
    )
    savings_rate = None

current_savings = st.sidebar.number_input(
    "Current Investments ($, negative for debt)", -1_000_000, 100_000_000, 0, 1_000,
    help="The current value of your investment portfolio or retirement savings. Enter negative if you have debt."
)

with st.sidebar.expander("Advanced Settings"):
    interest_on_debt = st.number_input(
        "Interest Rate on Debt (%)", 0.0, 100.0, 8.0, 0.1,
        help="Annual interest rate applied to your debt, if any."
    ) / 100
    rate_of_return = st.slider(
        "Real Rate of Return (%)", 0.0, 15.0, 7.0, 0.1,
        help="Expected annual return on investments after inflation."
    ) / 100
    withdrawal_rate = st.slider(
        "Withdrawal Rate (%)", 0.0, 10.0, 4.0, 0.1,
        help="Percentage of your portfolio you plan to withdraw each year during retirement."
    ) / 100
    other_income = st.number_input(
        "Other Retirement Income ($)", 0, 1_000_000, 0, 1_000,
        help="Other sources of retirement income, such as Social Security, pensions, or rental income."
    )

# ——— 2) Compute projections ———
df, ff_age = build_financials(
    age, goal_retirement_age,
    initial_salary, salary_growth_rate,
    mode, savings_rate, fixed_expenses,
    current_savings,
    interest_on_debt, rate_of_return, withdrawal_rate, other_income
)

# ——— 3) Render everything ———
render_visualizations(df, ff_age)

