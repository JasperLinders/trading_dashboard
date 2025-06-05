import pandas as pd

def compute_basic_stats(trade_data: pd.DataFrame) -> dict:
    """Compute basic statistics from trade data.
    """
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

    return {
        'num_trades': num_trades,
        'total_profit_loss': total_profit_loss,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'avg_win_loss_ratio': avg_win_loss_ratio,
        'expectancy': expectancy,
        'profit_factor': profit_factor
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