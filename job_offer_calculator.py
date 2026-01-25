import streamlit as st
from calculations import build_financials
import plotly.graph_objects as go

# ——— Color Scheme from Retirement Calculator ———
SPENDING_COLOR = "#D8F3DC"  # light mint
SAVINGS_COLOR  = "#95D5B2"  # mid green
TAXES_COLOR    = "#2D6A4F"  # deep forest

# ——— Page setup ———
st.set_page_config(page_title="Job Offer Evaluation", layout="wide")
st.title("Job Offer Evaluation")

# Control to add/remove offers
if 'jobs' not in st.session_state:
    st.session_state.jobs = [0]
cols_ctrl = st.columns([1,1,6])
with cols_ctrl[0]:
    if st.button("➕ Add Offer"):
        st.session_state.jobs.append(len(st.session_state.jobs))
with cols_ctrl[1]:
    if len(st.session_state.jobs) > 1:
        if st.button("➖ Remove Offer"):
            st.session_state.jobs.pop()

# ——— Main: Job Offer Inputs ———
st.write("---")
cols = st.columns(len(st.session_state.jobs))
job_configs = []
for idx, col in enumerate(cols):
    with col:
        st.subheader(f"Offer {idx+1}")
        # Personal Details
        age = st.number_input(
            "Current Age", 14, 100, 30, key=f"age_{idx}"
        )
        goal_ret = st.number_input(
            "Retirement Age", age+1, 120, 67, key=f"ret_{idx}"
        )
        # Salary
        name = st.text_input(
            "Job Name", value=f"Offer {idx+1}", key=f"name_{idx}"
        )
        init_sal = st.number_input(
            "Starting Salary ($)", 0, 1_000_000, 100_000, key=f"init_sal_{idx}"
        )
        g = st.number_input(
            "Salary Growth Rate (%)", 0, 100, 0"
        )
        # Contribution Method
        mode = st.radio(
            "Contribution Method", ["Savings Rate", "Fixed Expenses"], index=0,
            key=f"mode_{idx}"
        )
        if mode == "Savings Rate":
            savings_rate = st.slider(
                "Savings Rate (% of After-Tax Income)", 0, 100, 20,
                key=f"save_rate_{idx}"
            ) / 100
            fixed_exp = None
        else:
            fixed_exp = st.number_input(
                "Monthly Expenses ($)", 0, 1_000_000, 4_000,
                key=f"fixed_exp_{idx}"
            )
            savings_rate = None
        # Current Savings
        current_savings = st.number_input(
            "Current Investments ($)", -1_000_000, 100_000_000, 0,
            key=f"cur_save_{idx}"
        )
        # Advanced Settings
        with st.expander("Advanced Settings", expanded=False):
            interest_on_debt = st.number_input(
                "Interest Rate on Debt (%)", 0.0, 100.0, 8.0, 0.1,
                key=f"int_debt_{idx}"
            ) / 100
            rate_of_return = st.slider(
                "Real Rate of Return (%)", 0.0, 15.0, 7.0, 0.1,
                key=f"ror_{idx}"
            ) / 100
            withdrawal_rate = st.slider(
                "Withdrawal Rate (%)", 0.0, 10.0, 4.0, 0.1,
                key=f"wd_rate_{idx}"
            ) / 100
            other_income = st.number_input(
                "Other Income ($)", 0, 1_000_000, 0,
                key=f"oth_inc_{idx}"
            )
        job_configs.append({
            'name': name,
            'age': age,
            'ret_age': goal_ret,
            'initial_salary': init_sal,
            'end_salary': end_sal,
            'mode': mode,
            'savings_rate': savings_rate,
            'fixed_expenses': fixed_exp,
            'current_savings': current_savings,
            'interest_on_debt': interest_on_debt,
            'rate_of_return': rate_of_return,
            'withdrawal_rate': withdrawal_rate,
            'other_income': other_income
        })

# ——— Visualizations ———
st.write("---")
for title, drawer in [
    ("💸 Income, Taxes & Savings Over Time", 'financial'),
    ("💰 Net Worth Over Time", 'networth')
]:
    st.header(title)
    cols = st.columns(len(job_configs))
    for col, cfg in zip(cols, job_configs):
        df, _ = build_financials(
            cfg['age'], cfg['ret_age'],
            cfg['initial_salary'], cfg['end_salary'],
            cfg['mode'], cfg['savings_rate'], cfg['fixed_expenses'],
            cfg['current_savings'],
            cfg['interest_on_debt'], cfg['rate_of_return'],
            cfg['withdrawal_rate'], cfg['other_income']
        )
        fig = go.Figure()
        if drawer == 'financial':
            spending = df['Spending']
            savings = df['After-Tax Income'] - df['Spending']
            taxes   = df['Salary'] - df['After-Tax Income']
            fig.add_trace(go.Bar(x=df['Age'], y=spending, name='Spending', marker_color=SPENDING_COLOR))
            fig.add_trace(go.Bar(x=df['Age'], y=savings,  name='Savings',  marker_color=SAVINGS_COLOR))
            fig.add_trace(go.Bar(x=df['Age'], y=taxes,    name='Taxes',    marker_color=TAXES_COLOR))
            yaxis_title = 'Amount ($)'
        else:
            contrib = df['Contribution'].cumsum()
            growth  = df['Net Worth'] - contrib
            fig.add_trace(go.Bar(x=df['Age'], y=contrib, name='Contributions',     marker_color=SPENDING_COLOR))
            fig.add_trace(go.Bar(x=df['Age'], y=growth,  name='Investment Growth', marker_color=SAVINGS_COLOR))
            yaxis_title = 'Net Worth ($)'
        fig.update_layout(barmode='stack', xaxis_title='Age', yaxis_title=yaxis_title, yaxis_tickformat='$, .0f')
        with col:
            st.subheader(cfg['name'])
            st.plotly_chart(fig, use_container_width=True)

