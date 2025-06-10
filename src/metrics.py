import pandas as pd
import numpy as np

def add_mfe_mae_columns(trade_data: pd.DataFrame) -> pd.DataFrame:
    """
    Add new columns for MFE, MAE, and MFE/MAE ratio to the trade_data DataFrame.
    """
    trade_data = trade_data.copy()  # Avoid modifying original df

    is_long = trade_data['trade_type'] == 'Long'
    is_short = trade_data['trade_type'] == 'Short'

    # For Long trades
    # MFE = price_range_high - entry_price (max favorable excursion)
    # MAE = entry_price - price_range_low (max adverse excursion)
    trade_data.loc[is_long, 'mfe'] = trade_data.loc[is_long, 'price_range_high'] - trade_data.loc[is_long, 'entry_price']
    trade_data.loc[is_long, 'mae'] = trade_data.loc[is_long, 'entry_price'] - trade_data.loc[is_long, 'price_range_low']
    trade_data.loc[is_long, 'mfe_mae_ratio'] = trade_data.loc[is_long, 'mfe'] / trade_data.loc[is_long, 'mae']

    # For Short trades
    # MFE = entry_price - price_range_low
    # MAE = price_range_high - entry_price
    trade_data.loc[is_short, 'mfe'] = trade_data.loc[is_short, 'entry_price'] - trade_data.loc[is_short, 'price_range_low']
    trade_data.loc[is_short, 'mae'] = trade_data.loc[is_short, 'price_range_high'] - trade_data.loc[is_short, 'entry_price']
    trade_data.loc[is_short, 'mfe_mae_ratio'] = trade_data.loc[is_short, 'mfe'] / trade_data.loc[is_short, 'mae']

    # Handle division by zero or invalid values by replacing infinities and NaNs with None or 0
    trade_data['mfe_mae_ratio'].replace([float('inf'), -float('inf')], float('nan'), inplace=True)
    trade_data['mfe_mae_ratio'].fillna(0, inplace=True)

    return trade_data

def compute_basic_stats(trade_data: pd.DataFrame) -> dict:
    """Compute basic statistics from trade data.
    """
    trade_data = add_mfe_mae_columns(trade_data)

    num_trades = len(trade_data)
    total_profit_loss = trade_data['profit_loss'].sum()

    wins = trade_data[trade_data['profit_loss'] >= 0]['profit_loss']
    losses = trade_data[trade_data['profit_loss'] < 0]['profit_loss']

    win_rate = len(wins) / num_trades if num_trades > 0 else 0
    avg_win = wins.mean() if not wins.empty else 0
    avg_loss = losses.mean() if not losses.empty else 0
    avg_win_loss_ratio = avg_win / abs(avg_loss) if avg_loss != 0 else float('inf')
    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
    profit_factor = wins.sum() / abs(losses.sum()) if not losses.empty else float('inf')
    avg_mfe_mae_ratio = trade_data['mfe_mae_ratio'].mean() if not trade_data['mfe_mae_ratio'].empty else 0
    avg_mfe = trade_data['mfe'].mean() if not trade_data['mfe'].empty else 0
    avg_mae = trade_data['mae'].mean() if not trade_data['mae'].empty else 0

    return {
        'num_trades': num_trades,
        'total_profit_loss': total_profit_loss,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'avg_win_loss_ratio': avg_win_loss_ratio,
        'expectancy': expectancy,
        'profit_factor': profit_factor,
        'avg_mfe_mae_ratio': avg_mfe_mae_ratio,
        'avg_mfe': avg_mfe,
        'avg_mae': avg_mae
    }

def compute_advanced_stats(trade_data: pd.DataFrame) -> dict:
    """Compute advanced statistics from trade data.
    """
    total_profit_loss = trade_data['profit_loss'].sum()

    max_win = trade_data['profit_loss'].max()
    max_loss = trade_data['profit_loss'].min()

    cumulative_pnl = trade_data['profit_loss'].cumsum()
    max_drawdown = (pnl := trade_data['profit_loss'].cumsum()).sub(pnl.cummax()).min()
    relative_drawdown = abs(max_drawdown / total_profit_loss) if total_profit_loss > 0 else float('inf')

    avg_duration = trade_data['duration_sec'].mean()
    avg_duration_win = trade_data[trade_data['profit_loss'] >= 0]['duration_sec'].mean()
    avg_duration_loss = trade_data[trade_data['profit_loss'] < 0]['duration_sec'].mean()

    return {
        'cumulative_pnl': cumulative_pnl,
        'max_win': max_win,
        'max_loss': max_loss,
        'max_drawdown': max_drawdown,
        'relative_drawdown': relative_drawdown,
        'avg_duration': avg_duration,
        'avg_duration_win': avg_duration_win,
        'avg_duration_loss': avg_duration_loss
    }

def compute_daily_stats(trade_data: pd.DataFrame) -> pd.DataFrame:
    """Compute daily statistics from trade data.
    """
    # Group by date
    daily_pnl = trade_data.groupby("date")["profit_loss"].sum()

    # Daily stats
    avg_day_pnl = daily_pnl.mean()
    avg_win_day = daily_pnl[daily_pnl > 0].mean()
    avg_loss_day = daily_pnl[daily_pnl < 0].mean()
    days_traded = trade_data["date"].nunique()
    trades_per_day = trade_data.groupby("date").size()
    avg_trades_per_day = trades_per_day.mean() if not trades_per_day.empty else 0

    return {
        'daily_pnl': daily_pnl,
        'avg_day_pnl': avg_day_pnl,
        'avg_win_day': avg_win_day,
        'avg_loss_day': avg_loss_day,
        'days_traded': days_traded,
        'trades_per_day': trades_per_day,
        'avg_trades_per_day': avg_trades_per_day
    }

def compute_rolling_stats(trade_data: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """Compute rolling and expanding statistics from trade data."""
    metrics = compute_basic_stats(trade_data.iloc[:window])  # just to get keys
    for key in metrics:
        trade_data[f'expanding_{key}'] = np.nan
        trade_data[f'rolling_{key}'] = np.nan

    for i in range(window, len(trade_data)):
        expanding_sample = trade_data.iloc[:i+1]
        rolling_sample = trade_data.iloc[i-window:i+1]

        expanding_stats = compute_basic_stats(expanding_sample)
        rolling_stats = compute_basic_stats(rolling_sample)

        for key, value in expanding_stats.items():
            trade_data.loc[trade_data.index[i], f'expanding_{key}'] = value
        for key, value in rolling_stats.items():
            trade_data.loc[trade_data.index[i], f'rolling_{key}'] = value

    return trade_data