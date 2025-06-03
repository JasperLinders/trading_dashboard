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

    day_profit_loss = trade_data.groupby('date')['profit_loss'].sum()
    avg_day_profit_loss = day_profit_loss.mean()
    avg_winning_day_profit_loss = day_profit_loss[day_profit_loss > 0].mean()
    avg_losing_day_profit_loss = day_profit_loss[day_profit_loss < 0].mean()

    max_win = trade_data['profit_loss'].max()
    max_loss = trade_data['profit_loss'].min()

    cumulative_pnl = trade_data['profit_loss'].cumsum()
    max_drawdown = (pnl := trade_data['profit_loss'].cumsum()).sub(pnl.cummax()).min()
    relative_drawdown = abs(max_drawdown / total_profit_loss) if total_profit_loss > 0 else float('inf')

    avg_duration = trade_data['duration_sec'].mean()
    avg_duration_win = trade_data[trade_data['profit_loss'] >= 0]['duration_sec'].mean()
    avg_duration_loss = trade_data[trade_data['profit_loss'] < 0]['duration_sec'].mean()

    return {
        'avg_day_profit_loss': avg_day_profit_loss,
        'avg_winning_day_profit_loss': avg_winning_day_profit_loss,
        'avg_losing_day_profit_loss': avg_losing_day_profit_loss,
        'max_win': max_win,
        'max_loss': max_loss,
        'max_drawdown': max_drawdown,
        'relative_drawdown': relative_drawdown,
        'avg_duration': avg_duration,
        'avg_duration_win': avg_duration_win,
        'avg_duration_loss': avg_duration_loss
    }