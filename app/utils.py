import pandas as pd

def process_excel(file, sheet_name):
    """Loads a specific sheet from an Excel file into a DataFrame."""
    df = pd.read_excel(file, sheet_name=sheet_name)
    return df

def compare_columns(df1, df2, column1, column2):
    """Compares two columns from two different DataFrames."""
    col1_values = set(df1[column1].dropna().astype(str))
    col2_values = set(df2[column2].dropna().astype(str))

    differences = col1_values - col2_values
    return differences
