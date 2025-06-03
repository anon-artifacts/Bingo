import os
import pandas as pd


def load_data(path):
    """Load train and test data from CSV files."""
    data = pd.read_csv(path)
    # Separate columns into X and Y
    y_columns = [col for col in data.columns if col.endswith(('+', '-'))]
    x_columns = [
        col for col in data.columns 
        if col not in y_columns and not col.endswith('X')
    ]
    X = data[x_columns]
    Y = data[y_columns]
    
    return X, Y
