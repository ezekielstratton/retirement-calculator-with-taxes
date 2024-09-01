import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# Inject custom CSS
st.markdown("""
<style>
/* General styles for better readability */
body {
    color: #333333; /* A neutral dark color for text */
    background-color: #f5f5f5; /* Light background */
}

/* Adjust text for dark mode */
@media (prefers-color-scheme: dark) {
    body {
        color: #f5f5f5; /* Light text color for dark mode */
        background-color: #333333; /* Dark background */
    }
}

/* Styling for Streamlit components */
.stButton>button {
    background-color: #4CAF50; /* Green background for buttons */
    color: white; /* White text */
}

/* Dark mode button styling */
@media (prefers-color-scheme: dark) {
    .stButton>button {
        background-color: #1a73e8; /* Blue background for dark mode */
        color: white; /* White text */
    }
}

/* Styling other elements as needed... */
</style>
""", unsafe_allow_html=True)


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
    remaining_income = income
    
    for i in range(len(brackets)):
        min_income, max_income = brackets[i]
        rate = rates[i]
        
        if remaining_income <= 0:
            break
        
        taxable_income = min(max_income, income - deduction) - min_income
        
        if taxable_income > 0:
            tax += taxable_income * rate
        
        remaining_income -= (max_income - min_income)
    
    return tax

def income_tax(income):
    return calculate_tax(income, 'income')

def fica_tax(income):
    return calculate_tax(income, 'fica')

def capital_gains_tax(income):
    return calculate_tax(income, 'capital_gains')

# Streamlit app title
st.title("Retirement Calculator")

# Input fields with "More info" expanders
with st.sidebar:
    
    # Enter your current age
    age = st.number_input("Enter your current age", key="age", min_value=14, max_value=100, value=30)
    with st.expander("More info about Age"):
        st.write("Enter your current age or the age you plan on starting your career \
                 . This is used as a starting point for calculating your financial trajectory.")
    #st.text("")  # Add space after the expander
    
    st.markdown("---")
    
    # Enter your initial annual salary
    initial_salary = st.number_input("Enter your initial annual salary", key="initial_salary", min_value=0, max_value=10000000, value=52000)
    with st.expander("More info about Initial Salary"):
        st.write("Your current or starting annual salary. This is the baseline for \
                 future salary growth calculations.")
    #st.text("")  # Add space after the expander
    st.markdown("---")
    
    # Select your savings rate
    savings_rate = st.slider("Select your savings rate (%)", key="savings_rate", min_value=0, max_value=99, value=20)/100
    with st.expander("More info about Savings Rate"):
        st.write("The portion of your salary that you plan to save. This rate \
                 directly impacts your savings growth over time.")
    #st.text("")  # Add space after the expander
    st.markdown("---")
    
    # Enter your current savings
    current_savings = st.number_input("Enter the total value of your current Investments (negative for debt) ", key="current_savings", min_value=-1000000, max_value=100000000, value=0)
    with st.expander("More info about Current Savings"):
        st.write("Your current total savings, plus your investments, minus any debt you have excluding your mortgage.\
                 This forms the starting point for calculating future investment growth.")
    #st.text("")  # Add space after the expander
    st.markdown("---")
    
    interest_on_debt = st.number_input("Enter the interest rate you'd like to use for debt (optional)"\
                                      , key="interest_on_debt", min_value=0.0, max_value=100.0, step=0.01, value=8.0)/100
    with st.expander("More info about Interest on Debt"):
        st.write("The interest rate you pay on any debt you have. This calculator assumes that \
                 you will pay off all your debt before you make investments. If you have \
                multiple loans with different interest rates, try using a weighted average.\
                You could also just use your highest interest rate to get a conservative estimate.\
                There is currently no consideration for the interest write off on student loans.")
    #st.text("")  # Add space after the expander
    st.markdown("---")
    
    with st.expander("Advanced Options"):
        
        # Expected annual rate of return on investments
        rate_of_return = st.number_input("Expected annual real rate of return on investments (%)", key="rate_of_return", min_value=0.0, max_value=20.0,step = 0.1, value=7.0)/100
        st.markdown("Learn more about rate of return",help="The expected annual return rate on your investments minus inflation.\
                   This impacts the growth of your savings and investments. Over the\
                   last 20 years the s&p 500, a common index fund and benchmark for stock returns,\
                    has produced about a 7% return after accounting for inflation. If you plan\
                    on holding a significant amount of your net worth in cash or bonds you\
                    should use a more conservative rate of return, like 0.04 or 0.05.")
        #st.text("")  # Add space after the expander
        st.markdown("---")
            
        # Withdrawal Rate
        withdrawal_rate = st.number_input("Withdrawal Rate (%)", key="withdrawal_rate", min_value= 0.00, max_value=10.00,step = 0.1, value=3.5)/100
        st.caption("Enter the percentage of your assets you plan on withdrawing yearly\
                   during retirement. Most people use the 4% rule")
        #st.text("")  # Add space after the expander
        st.markdown("---")
        
        # Expected annual salary growth rate
        salary_growth = st.number_input("Expected annual salary growth rate (%)", key="salary_growth", min_value=0.0, max_value=40.0,step = 0.1, value=1.0)/100
        st.caption("The annual percentage increase in your salary. This rate affects \
                     how your salary is projected to grow over time.")
        #st.text("")  # Add space after the expander
        st.markdown("---")
        
        # Diminish salary growth to zero
        checkbox_state = st.checkbox("Diminish salary growth to zero", key="checkbox_state")
        st.caption("If checked, this option adjusts the salary growth to gradually \
                     reduce to zero by the time of retirement. This is useful for\
                    career paths with high early career income growth which\
                        slows down after making partner or managing director such as\
                        finance, consulting, tech, law, and public accounting.")
        #st.text("")  # Add space after the expander
        st.markdown("---")
        
        # Other retirement income
        other_income = st.number_input("Other retirement income", key="other_income", min_value=0, max_value=10000000, value=0)
        st.caption("Enter any other income you expect to recieve during retirement \
                     here. This may include pensions of social security, or you can\
                     leave it blank to recieve a conservative estimate of retirement income.")
        #st.text("")  # Add space after the expander
        st.markdown("---")
    
        # Other retirement income
        life_expectancy = st.number_input("Life Expectancy", key="life_expectancy", min_value=age, max_value=120, value=79)
        st.caption("Enter how long you expect to live.")
        #st.text("")  # Add space after the expander
        st.markdown("---")

career_length = life_expectancy - age
df = pd.DataFrame({'Year': range(1, life_expectancy - age + 1)})

if checkbox_state:
    start_year = df['Year'].min()
    end_year = df['Year'].max()
    total_years = end_year - start_year
    df['Salary'] = initial_salary * (1 + salary_growth - salary_growth * (1/2) * (df['Year'] - start_year) / total_years) ** (df['Year'] - start_year)
else:
    df['Salary'] = initial_salary * (1 + salary_growth - (salary_growth / df['Year'])) ** (df['Year'] - 1)

df['Income Tax'] = df['Salary'].apply(income_tax)
df['FICA Tax'] = df['Salary'].apply(fica_tax)
df['Total Annual Tax'] = df['Income Tax'] + df['FICA Tax']
df['After Tax Income'] = df['Salary'] - df['Total Annual Tax']
df['Retirement Contribution'] = df['After Tax Income'] * savings_rate
df['Net Worth'] = 0
df.loc[0, 'Net Worth'] = df.loc[0, 'Retirement Contribution'] + current_savings

for i in range(1, len(df)):
    if df.loc[i - 1, 'Net Worth'] >= 0:
        df.loc[i, 'Net Worth'] = df.loc[i, 'Retirement Contribution'] + (df.loc[i - 1, 'Net Worth']) * (1 + rate_of_return)
    else:
        df.loc[i, 'Net Worth'] = df.loc[i, 'Retirement Contribution'] + (df.loc[i - 1, 'Net Worth']) * (1 + interest_on_debt)

df['Spending'] = df['After Tax Income'] - df['Retirement Contribution']
df['Investment Income'] = df['Net Worth'] * withdrawal_rate
df['Age'] = df['Year'] + age

df = df.round(0).astype(int)

# Calculate the differences between Investment Income and Spending
difference = df['Investment Income'] - df['Spending']
intersection_idx = np.where(np.diff(np.sign(difference)))[0]

if intersection_idx.size > 0:

    # Get the year of the first intersection
    intersection_year = df['Age'].iloc[intersection_idx[0] + 1]
    investment_income_at_intersection = df['Investment Income'].iloc[intersection_idx[0] + 1]
    st.markdown(
    f"<h2 style='color: black;'>Financial Freedom at age: {intersection_year}<br> Investment income ${investment_income_at_intersection:,} per year </h2>",
    unsafe_allow_html=True
    )    
    fig, ax = plt.subplots()
    plt.style.use('fivethirtyeight')
    plt.rcParams['font.family'] = 'Segoe UI'

    # Plot the Spending line
    ax.plot(df['Age'], df['Spending'], color='blue', label='Spending')

    # Plot withdrawal rate
    ax.plot(df['Age'], df['Investment Income'], color='green', label='Investment Income')
    
    # Fill the area between Spending and Investment Income with red
    ax.fill_between(df['Age'], df['Spending'], df['Investment Income'], where=(df['Spending'] > df['Investment Income']), color='red', alpha=0.3, interpolate=True)
   
    # Fill the area under the Investment Income line with a lighter shade of green
    ax.fill_between(df['Age'], df['Investment Income'], color='green', alpha=0.3)

    # Add a dashed line at the intersection point
    ax.axvline(x=intersection_year, color='red', linestyle='--', label=f'Financial Freedom at Age {intersection_year}')

    ax.set_xlabel('Age')
    ax.set_ylabel('Amount')
    ax.set_title('Income Over Time')
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'${int(x):,}'))
    ax.legend()

    st.pyplot(fig)
else:
    st.markdown(
    "<h2 style='color: red;'>Investment Income is never enough to sustain spending. Try saving more if possible.</h2>",
    unsafe_allow_html=True
    )    
    # Get the year of the first intersection
    fig, ax = plt.subplots()
    plt.style.use('fivethirtyeight')
    plt.rcParams['font.family'] = 'Segoe UI'

    # Plot the Spending line
    ax.plot(df['Age'], df['Spending'], color='blue', label='Spending')

    # Plot withdrawal rate
    ax.plot(df['Age'], df['Investment Income'], color='green', label='Investment Income')
    # Fill the area between Spending and Investment Income with red
    ax.fill_between(df['Age'], df['Spending'], df['Investment Income'], where=(df['Spending'] > df['Investment Income']), color='red', alpha=0.3, interpolate=True)
    # Fill the area under the Investment Income line with a lighter shade of green
    ax.fill_between(df['Age'], df['Investment Income'], color='green', alpha=0.3)


    # Add a dashed line at the intersection point
    ax.set_xlabel('Age')
    ax.set_ylabel('Amount')
    ax.set_title('Income Over Time')
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'${int(x):,}'))
    ax.legend()

    st.pyplot(fig)

# Display results with formatted values
# st.markdown(f"<b style='font-size: 20px;'>After Tax Career Earnings: ${sum(df['After Tax Income']):,.2f}</b>", unsafe_allow_html=True)
# st.markdown(f"<b style='font-size: 20px;'>Lifetime Tax Paid: ${sum(df['Total Annual Tax']):,.2f}</b>", unsafe_allow_html=True)
# st.markdown(f"<b style='font-size: 20px;'>Lifetime Spending: ${sum(df['Spending']) + df['Investment Income'].iloc[-1] * (life_expectancy - suggested_retirement_age):,.2f}</b>", unsafe_allow_html=True)

# Calculate the cumulative contributions
df['Cumulative Contributions'] = df['Retirement Contribution'].cumsum()

# Update the Plot for Net Worth Over Time with Shaded Areas
fig, ax = plt.subplots()
plt.style.use('fivethirtyeight')
plt.rcParams['font.family'] = 'Segoe UI'

ax.plot(df['Age'], df['Net Worth'], label='Net Worth')
ax.fill_between(df['Age'], 0, df['Cumulative Contributions'], color='skyblue', alpha=0.5, label='Contributions')
ax.fill_between(df['Age'], df['Cumulative Contributions'], df['Net Worth'], color='orange', alpha=0.5, label='Investment Growth')

ax.set_xlabel('Age')
ax.set_ylabel('Amount')
ax.set_title('Net Worth Over Time')
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'${int(x):,}'))
ax.legend()

st.pyplot(fig)

fig, ax = plt.subplots()
plt.style.use('fivethirtyeight')
plt.rcParams['font.family'] = 'Segoe UI'

ax.plot(df['Age'], df['Salary'], label='Salary', color='red')
ax.plot(df['Age'], df['Spending'], color='blue', label='Spending')

ax.fill_between(df['Age'], df['Spending'] + df['Retirement Contribution'], df['Salary'], color='red', alpha=0.2, label='Taxes')
ax.fill_between(df['Age'], df['Spending'], df['Spending'] + df['Retirement Contribution'], color='green', alpha=0.2, label='Savings')
ax.fill_between(df['Age'], 0, df['Spending'], color='blue', alpha=0.2)

ax.set_xlabel('Age')
ax.set_ylabel('Amount')
ax.set_title('Income Over Time')
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'${int(x):,}'))
ax.legend()

st.pyplot(fig)

df = df.set_index('Age')
st.dataframe(df)
