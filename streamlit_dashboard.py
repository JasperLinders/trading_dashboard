import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data_loader import load_trade_data
from src.metrics import *

# --- Page Setup ---
st.set_page_config(page_title="Trading Dashboard", layout="wide")

# --- Load Data ---
df = load_trade_data('trades_synthetic.csv')

# --- Compute Stats ---
basic_stats = compute_basic_stats(df)
advanced_stats = compute_advanced_stats(df)
daily_stats = compute_daily_stats(df)

# --- Page Title ---
st.title("📈 Trading Performance Dashboard")

# --- Key Stats: Single Row ---
st.subheader("Key Statistics")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Trades", basic_stats["num_trades"])
k2.metric("Win Rate", f"{basic_stats['win_rate']:.1%}")
k3.metric("Avg Win/Loss", f"{basic_stats['avg_win_loss_ratio']:.2f}", help="Average win / average loss")
k4.metric("Expectancy", f"${basic_stats['expectancy']:.2f}", help="Expected PnL per trade")


# --- PnL Section ---
st.markdown("---")
st.subheader("Performance Overview")
left, right = st.columns([3, 1])

# Left: Cumulative PnL Plot
fig = px.line(
    x=df.index,
    y=advanced_stats["cumulative_pnl"],
    labels={"x": "Trade Index", "y": "PnL ($)"},
    title="Cumulative PnL"
)
fig.update_layout(
    margin=dict(l=0, r=0, t=30, b=0),
    shapes=[dict(
        type='line',
        xref='paper',
        x0=0, x1=1,
        yref='y',
        y0=0, y1=0,
        line=dict(color='gray', width=1, dash='dash')
    )],
    template='plotly_dark',
    height=400,
)
left.plotly_chart(fig, use_container_width=True)

# Right: Total PnL and Avg Win/Loss
total_pnl = basic_stats["total_profit_loss"]

with right:
    st.markdown("<div style='margin-top: 50px;'>", unsafe_allow_html=True)

    pnl_color = "lime" if total_pnl >= 0 else "tomato"
    st.markdown(
        f"<div style='text-align:center; font-size:36px; font-weight:bold; color:{pnl_color}; margin-bottom:0px;'>${total_pnl:.2f}</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='text-align:center; font-size:20px; color:#ccc; margin-bottom:20px;'>Total PnL</div>",
        unsafe_allow_html=True
    )

    # First row: Avg Win / Avg Loss
    row1 = st.columns(2)
    row1[0].markdown(f"<div style='text-align:center; font-size:20px; font-weight:bold; color:#eee;'>${basic_stats['avg_win']:.2f}</div>", unsafe_allow_html=True)
    row1[0].markdown("<div style='text-align:center; font-size:14px; color:#aaa;'>Average Win</div>", unsafe_allow_html=True)

    row1[1].markdown(f"<div style='text-align:center; font-size:20px; font-weight:bold; color:#eee;'>${basic_stats['avg_loss']:.2f}</div>", unsafe_allow_html=True)
    row1[1].markdown("<div style='text-align:center; font-size:14px; color:#aaa;'>Average Loss</div>", unsafe_allow_html=True)

    # Add spacing
    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)

    # Second row: Max Win / Max Loss
    row2 = st.columns(2)
    row2[0].markdown(f"<div style='text-align:center; font-size:20px; font-weight:bold; color:#eee;'>${advanced_stats['max_win']:.2f}</div>", unsafe_allow_html=True)
    row2[0].markdown("<div style='text-align:center; font-size:14px; color:#aaa;'>Max Win</div>", unsafe_allow_html=True)

    row2[1].markdown(f"<div style='text-align:center; font-size:20px; font-weight:bold; color:#eee;'>${advanced_stats['max_loss']:.2f}</div>", unsafe_allow_html=True)
    row2[1].markdown("<div style='text-align:center; font-size:14px; color:#aaa;'>Max Loss</div>", unsafe_allow_html=True)

    # Spacer
    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)

    # Third row: Max Drawdown
    row3 = st.columns(1)
    row3[0].markdown(f"<div style='text-align:center; font-size:20px; font-weight:bold; color:#eee;'>${advanced_stats['max_drawdown']:.2f}</div>", unsafe_allow_html=True)
    row3[0].markdown("<div style='text-align:center; font-size:14px; color:#aaa;'>Max Drawdown</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# --- Daily PnL Section ---
st.markdown("---")
st.subheader("📅 Daily PnL Overview")


# Layout: Left = Bar Plot, Right = Stats
left, right = st.columns([3, 1])

with left:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.75, 0.25],  # smaller height for trades plot
        subplot_titles=("Daily PnL ($)", "Number of Trades")
    )

    # Daily PnL bars
    fig.add_trace(
        go.Bar(
            x=daily_stats['daily_pnl'].index,
            y=daily_stats['daily_pnl'].values,
            marker_color=['green' if v >= 0 else 'red' for v in daily_stats['daily_pnl'].values],
            name='Daily PnL',
        ),
        row=1, col=1
    )

    # Number of trades bars
    fig.add_trace(
        go.Bar(
            x=daily_stats['trades_per_day'].index,
            y=daily_stats['trades_per_day'].values,
            marker_color='gray',
            name='Trades per Day',
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=500,  # slightly less height overall
        showlegend=False,
        margin=dict(l=0, r=0, t=40, b=30),
        template='plotly_dark',
        bargap=0.6,
        bargroupgap=0.1,
    )

    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="PnL ($)", row=1, col=1)
    fig.update_yaxes(title_text="Trades", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

# Stats to the side, matching PnL style
with right:
    st.markdown("<div style='margin-top: 50px;'>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)  # Spacer

    st.markdown(f"<div style='text-align:center; font-size:20px; font-weight:bold; color:#eee;'>{daily_stats['days_traded']}</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; font-size:14px; color:#aaa;'>Days Traded</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)  # Spacer

    st.markdown(f"<div style='text-align:center; font-size:20px; font-weight:bold; color:#eee;'>{daily_stats['avg_trades_per_day']:.1f}</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; font-size:14px; color:#aaa;'>Average Trades Per Day</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)  # Spacer

    st.markdown(f"<div style='text-align:center; font-size:20px; font-weight:bold; color:#eee;'>${daily_stats['avg_day_pnl']:.2f}</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; font-size:14px; color:#aaa;'>Average Day PnL</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)

    st.markdown(f"<div style='text-align:center; font-size:20px; font-weight:bold; color:#eee;'>${daily_stats['avg_win_day']:.2f}</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; font-size:14px; color:#aaa;'>Average Winning Day</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)

    st.markdown(f"<div style='text-align:center; font-size:20px; font-weight:bold; color:#eee;'>${daily_stats['avg_loss_day']:.2f}</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; font-size:14px; color:#aaa;'>Average Losing Day</div>", unsafe_allow_html=True)


# ---  ---


















# # --- Trader Profile ---
# def plot_trader_profile(win_rate, avg_win_loss_ratio):
#     x = np.linspace(0.01, 0.99, 300)
#     y = (1 - x) / x

#     fig = go.Figure()

#     fig.add_trace(go.Scatter(
#         x=x, y=y,
#         mode='lines',
#         name='Breakeven',
#         line=dict(color='gray', dash='dash')
#     ))

#     fig.add_trace(go.Scatter(
#         x=[win_rate],
#         y=[avg_win_loss_ratio],
#         mode='markers+text',
#         name='You',
#         marker=dict(color='deepskyblue', size=14, line=dict(color='white', width=2)),
#         text=['You'],
#         textposition='top center'
#     ))

#     fig.update_layout(
#         xaxis_title='Win Rate',
#         yaxis_title='Avg Win / Avg Loss',
#         xaxis=dict(range=[0.2, 0.8]),
#         yaxis=dict(range=[0, 4]),
#         template='plotly_dark',
#         height=400,
#         width=600,
#         margin=dict(l=40, r=40, t=40, b=40)
#     )
#     return fig

# st.markdown("---")
# st.subheader("Trader Profile")
# fig = plot_trader_profile(basic_stats['win_rate'], basic_stats['avg_win_loss_ratio'])
# st.plotly_chart(fig, use_container_width=True)