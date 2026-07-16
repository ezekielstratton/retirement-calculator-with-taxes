import streamlit as st
import plotly.graph_objects as go

def render_visualizations(df, ff_age):
    # Dark mode toggle
    dark_mode = st.sidebar.checkbox("Dark Mode", True)
    if dark_mode:
        label_color = 'white'
        plotly_template = 'plotly_dark'
    else:
        label_color = 'black'
        plotly_template = 'plotly_white'

    # Monochrome green palette
    spending_color = "#D8F3DC"  # light mint
    savings_color  = "#95D5B2"  # mid green
    taxes_color    = "#2D6A4F"  # deep forest

    # ——— 1) Taxes & Savings Breakdown ———
    st.header("💸 Salary, Taxes & Savings Over Time")
    # compute bar segments
    spending_vals = df['Spending']
    savings_vals  = df['After-Tax Income'] - df['Spending']
    taxes_vals    = df['Salary'] - df['After-Tax Income']
    # interactive stacked bar chart
    fig = go.Figure()
    # Spending trace
    fig.add_trace(go.Bar(
        x=df['Age'],
        y=spending_vals,
        name='Spending',
        marker_color=spending_color,
        hovertemplate='$%{y:,.0f}<extra>Spending</extra>'
    ))
    # Savings trace
    fig.add_trace(go.Bar(
        x=df['Age'],
        y=savings_vals,
        name='Savings',
        marker_color=savings_color,
        hovertemplate='$%{y:,.0f}<extra>Savings</extra>'
    ))
    # Taxes trace
    fig.add_trace(go.Bar(
        x=df['Age'],
        y=taxes_vals,
        name='Taxes',
        marker_color=taxes_color,
        hovertemplate='$%{y:,.0f}<extra>Taxes</extra>'
    ))
    # styling
    fig.update_layout(
        barmode='stack',
        template=plotly_template,
        xaxis_title='Age',
        yaxis_title='Amount ($)',
        yaxis_tickformat='$,.0f',
        legend_title_text='',
        font_family="Source Sans Pro",
        font_color=label_color
    )
    st.plotly_chart(fig, use_container_width=True)

    # ——— 2) Results Overview ———
    st.header("📊 Results Overview")
    if ff_age:
        st.success(f"🎉 You can achieve financial freedom at age **{ff_age}**!")

    # display retirement-age metrics with header-sized fonts
    last_age      = int(df['Age'].max())
    ret_income    = df.loc[df['Age'] == last_age, 'Investment Income'].iloc[0]
    ret_net_worth = df.loc[df['Age'] == last_age, 'Net Worth'].iloc[0]
    c1, c2 = st.columns(2)
    with c1:
        st.header("Passive Investment Income at Retirement Age:")
        st.subheader(f"${ret_income:,.0f}")
    with c2:
        st.header("Net Worth at Retirement Age:")
        st.subheader(f"${ret_net_worth:,.0f}")

    # ——— 3) Net Worth Breakdown ———
    st.header("💰 Net Worth: Contributions vs. Investment Growth")
    # prepare components
    cum_contrib = df['Contribution'].cumsum()
    growth_vals = df['Net Worth'] - cum_contrib
    # interactive stacked bar chart
    fig1 = go.Figure()
    # Contributions trace
    fig1.add_trace(go.Bar(
        x=df['Age'],
        y=cum_contrib,
        name='Contributions',
        marker_color=spending_color,
        hovertemplate='$%{y:,.0f}<extra>Contributions</extra>'
    ))
    # Investment Growth trace
    fig1.add_trace(go.Bar(
        x=df['Age'],
        y=growth_vals,
        name='Investment Growth',
        marker_color=savings_color,
        hovertemplate='$%{y:,.0f}<extra>Investment Growth</extra>'
    ))
    # styling
    fig1.update_layout(
        barmode='stack',
        template=plotly_template,
        xaxis_title='Age',
        yaxis_title='Net Worth ($)',
        yaxis_tickformat='$,.0f',
        legend_title_text='',
        font_family="Source Sans Pro",
        font_color=label_color
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Summary for chart 3
    contrib_end = cum_contrib.iloc[-1]
    growth_end  = growth_vals.iloc[-1]
    st.markdown(
        f"**Summary:** By retirement age {last_age}, you'll have contributed "
        f"${contrib_end:,.0f}$ and earned ${growth_end:,.0f}$ in investment growth, "
        f"for a total net worth of ${ret_net_worth:,.0f}."
    )

    # ——— 4) Passive Income vs. Spending ———
    st.header("💡 Passive Income vs. Spending")
    # interactive grouped bar chart
    fig2 = go.Figure()
    # Spending trace
    fig2.add_trace(go.Bar(
        x=df['Age'],
        y=df['Spending'],
        name='Spending',
        marker_color=spending_color,
        hovertemplate='$%{y:,.0f}<extra>Spending</extra>'
    ))
    # Investment Income trace
    fig2.add_trace(go.Bar(
        x=df['Age'],
        y=df['Investment Income'],
        name='Investment Income',
        marker_color=savings_color,
        hovertemplate='$%{y:,.0f}<extra>Investment Income</extra>'
    ))
    # financial freedom line
    if ff_age:
        fig2.add_vline(
            x=ff_age,
            line_dash='dash',
            line_color='#006400',
            annotation_text=f"Financial Freedom at Age {ff_age}",
            annotation_position='top right'
        )
    # styling & axis limit
    fig2.update_layout(
        barmode='group',
        template=plotly_template,
        xaxis_title='Age',
        yaxis_title='Amount ($)',
        yaxis_tickformat='$,.0f',
        legend_title_text='',
        font_family="Source Sans Pro",
        font_color=label_color,
        xaxis=dict(range=[df['Age'].min(), last_age])
    )
    st.plotly_chart(fig2, use_container_width=True)


    # ——— 5) Detailed Projections & Metrics ———
    st.subheader("Detailed Financial Projections")
    df_display = df.set_index('Age')[[
        'Salary', 'After-Tax Income', 'Spending',
        'Contribution', 'Net Worth', 'Investment Income'
    ]]
    st.dataframe(df_display.style.format('${:,.0f}'))
