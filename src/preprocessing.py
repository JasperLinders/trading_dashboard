import pandas as pd
from src.config import RAW_DATA_DIR

def preprocess_raw_data(file_name: str = "TradesList.txt") -> pd.DataFrame:
    """Load and preprocess raw data from a CSV file.
    """
    # Load the raw data
    raw_data = pd.read_csv(RAW_DATA_DIR / f"{file_name}", sep='\t')

    # Drop unnecessary columns
    raw_data.drop(columns=['Max Open Quantity',
                         'Max Closed Quantity',
                         'Cumulative Profit/Loss (C)',
                         'FlatToFlat Profit/Loss (C)',
                         'FlatToFlat Max Open Profit (C)',
                         'FlatToFlat Max Open Loss (C)',
                         'Max Open Profit (C)',
                         'Max Open Loss (C)',
                         'Entry Efficiency',
                         'Exit Efficiency',
                         'Total Efficiency',
                         'Note',
                         'Open Position Quantity',
                         'Close Position Quantity'],
                         inplace=True)
    
    # Drop empty rows
    raw_data.dropna(axis=0, inplace=True)

    # Rename columns
    raw_data.rename(columns={'Symbol': 'symbol',
                                'Trade Type': 'trade_type',
                                'Entry DateTime': 'entry_datetime',
                                'Exit DateTime': 'exit_datetime',
                                'Entry Price': 'entry_price',
                                'Exit Price': 'exit_price',
                                'Trade Quantity': 'quantity',
                                'Profit/Loss (C)': 'profit_loss',
                                'Commission (C)': 'commission',
                                'High Price While Open': 'price_range_high',
                                'Low Price While Open': 'price_range_low',
                                'Duration': 'duration'}, inplace=True)
    
    # Clean the symbol string
    raw_data['symbol'] = raw_data['symbol'].apply(
        lambda x: x.split(']')[-1].split('-')[0].strip().split(' ')[0][0:3]
    )

    # Convert datetime columns to datetime type
    raw_data['entry_datetime'] = pd.to_datetime(
        raw_data['entry_datetime'].str.replace(' BP', '', regex=False)
    )
    raw_data['exit_datetime'] = pd.to_datetime(
        raw_data['exit_datetime'].str.replace(' EP', '', regex=False)
    )

    # Convert duration column to timedelta type
    raw_data['duration_sec'] = pd.to_timedelta(raw_data['duration']).dt.total_seconds()
    raw_data.drop(columns=['duration'], inplace=True)

    # Add simple date column for convenience of stats computation
    raw_data['date'] = raw_data['entry_datetime'].dt.date

    # Order by entry datetime
    raw_data.sort_values(by='entry_datetime', inplace=True)

    # Reset index after sorting
    raw_data.reset_index(drop=True, inplace=True)

    # Create a clean copy of the data
    clean_data = raw_data.copy()

    return clean_data