import pandas as pd
import numpy as np

# ——— 2025 Tax configuration constants ———
TAX_BRACKETS = {
    'income': [
        (0, 11925),            # 10% up to $11,925
        (11925, 48475),        # 12% $11,925–$48,475
        (48475, 103350),       # 22% $48,475–$103,350
        (103350, 197300),      # 24% $103,350–$197,300
        (197300, 250525),      # 32% $197,300–$250,525
        (250525, 626350),      # 35% $250,525–$626,350
        (626350, float('inf')) # 37% over $626,350
    ],
    'fica': [
        (0, 160000)            # 7.65% FICA up to $160,000
    ],
    'capital_gains': [
        (0,       48350),      # 0% up to $48,350
        (48351,   533400),     # 15% $48,351–$533,400
        (533401,  float('inf'))# 20% over $533,400
    ]
}

TAX_RATES = {
    'income': [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37],
    'fica': [0.0765],
    'capital_gains': [0.0, 0.15, 0.20]
}

DEDUCTIONS = {
    'income': 15000,
    'fica': 0,
    'capital_gains': 0
}

def calculate_tax(income, tax_type):
    brackets, rates, deduction = TAX_BRACKETS[tax_type], TAX_RATES[tax_type], DEDUCTIONS[tax_type]
    tax, taxable = 0, max(0, income - deduction)
    for (min_i, max_i), rate in zip(brackets, rates):
        if taxable > min_i:
            tax += (min(taxable, max_i) - min_i) * rate
        else:
            break
    return tax

def build_financials(
    age, goal_retirement_age,
    initial_salary, salary_growth_rate,
    mode, savings_rate, fixed_expenses,
    current_savings,
    interest_on_debt, rate_of_return, withdrawal_rate, other_income
):
    # Projection period
    years = max(1, goal_retirement_age - age)

    # Build DataFrame
    df = pd.DataFrame({'Year': range(1, years+1)})
    df['Age'] = age + df['Year'] - 1

 #   # Salary Projection with decaying salary growth rate
 #   # Salary growth as a % is higher early on, this function accounts for that
 #   # We solve for a function whose growth rate = 0 at retirement age
 #   # total span (years-1)
 #   T = years - 1
 #   # time since start
 #   t = df['Year'] - 1
    
    # Compute r₀ so that ∫₀ᵀ r(t) dt = ln(end/initial)
    # and let r(t) = r₀ · (1 – t/T) so that r(T)=0
 #   r0 = 2 * np.log(end_salary / initial_salary) / T
    
    # Closed-form solution of dS/dt = r(t)·S
 #   df['Salary'] = initial_salary * np.exp(
 #       r0 * (t - t**2/(2*T))
 #   )
    # Salary projection: simple compounded annual growth
    t = (df['Year'] - 1).clip(lower=0)  # periods since start
    df['Salary'] = initial_salary * (1.0 + salary_growth_rate) ** t
    # Tax calculations
    df['Income Tax']      = df['Salary'].apply(lambda i: calculate_tax(i, 'income'))
    df['FICA Tax']        = df['Salary'].apply(lambda i: calculate_tax(i, 'fica'))
    df['Total Tax']       = df['Income Tax'] + df['FICA Tax']
    df['After-Tax Income']= df['Salary'] - df['Total Tax']

    # Contribution and Spending
    def _cs(row):
        ati = row['After-Tax Income']
        if mode == "Savings Rate":
            c = ati * savings_rate
            s = ati - c
        else:
            s = fixed_expenses
            c = max(0, ati - fixed_expenses)
        return pd.Series({'Contribution': c, 'Spending': s})
    df[['Contribution','Spending']] = df.apply(_cs, axis=1)

    # Net Worth
    df['Net Worth'] = 0
    df.loc[0,'Net Worth'] = current_savings + df.loc[0,'Contribution']
    for i in range(1, len(df)):
        prev    = df.loc[i-1,'Net Worth']
        contrib = df.loc[i,'Contribution']
        r       = rate_of_return if prev>=0 else -interest_on_debt
        df.loc[i,'Net Worth'] = prev*(1+r) + contrib

    # Investment Income and Freedom age
    df['Investment Income'] = df['Net Worth']*withdrawal_rate + other_income
    df['Freedom'] = df['Investment Income'] >= df['Spending']
    ff     = df[df['Freedom']]
    ff_age = int(ff.iloc[0]['Age']) if not ff.empty else None

    return df, ff_age


