# Constrained Mean-Variance Portfolio Optimizer

A Streamlit app for **constrained mean-variance (Markowitz) portfolio optimization**. Choose assets with expected return and volatility, set constraints (no short selling, max weight per asset), and compute the efficient frontier plus an optimal portfolio (max Sharpe ratio, min variance, or target return).

## Features

- **Inputs:** Per-asset expected return (%) and volatility (%). Correlation between assets is set via a single parameter to build the covariance matrix.
- **Constraints:** Weights sum to 1; optional no short selling (weights ≥ 0); optional cap on maximum weight per asset.
- **Objectives:** Maximize Sharpe ratio, minimize variance for a target return, or minimize variance only.
- **Outputs:** Efficient frontier (return vs volatility), optimal weights (bar chart and table), and portfolio metrics (return, volatility, Sharpe ratio).

## How to run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the app:
   ```bash
   streamlit run retirement-calculator-app.py
   ```
3. Use the sidebar to pick sample assets or define your own (name, expected return %, volatility %). Set correlation, risk-free rate, and constraints, then choose the optimization target. The main area shows the efficient frontier and the optimal portfolio.

## Requirements

- Python 3.x
- streamlit, pandas, numpy, plotly, scipy
