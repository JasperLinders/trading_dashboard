import pandas as pd
from src.config import PROCESSED_DATA_DIR

# Load the trades data
def load_trade_data(file_name: str = "trades.csv") -> pd.DataFrame:
    """Load trade data from a CSV file.
    """
    trade_data = pd.read_csv(PROCESSED_DATA_DIR / f"{file_name}")
    return trade_data