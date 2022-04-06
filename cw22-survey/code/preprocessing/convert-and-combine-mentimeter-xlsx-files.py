from pathlib import Path

import numpy as np
import pandas as pd

# Set directory paths
ABSOLUTE_HERE = Path(__file__).parent
raw_data_dir = ABSOLUTE_HERE.parent.parent.joinpath("data/raw")
processed_data_dir = ABSOLUTE_HERE.parent.parent.joinpath("data/processed")

# Columns we don't need for analysis
cols_to_drop = ["Session", "How to join this survey:", "Thank You!:"]

# Columns that contain free text responses
open_questions = [
    "If you publish code",
    "If you don't publish code",
    "Which environment management tools",
    "Which tools",
]

# Date the survey was conducted
date_to_filter_on = "2022-04-06"

# Empty dataframe to combine responses into
df = pd.DataFrame({})

# Find raw xlsx files
for i, filename in enumerate(raw_data_dir.glob("*.xlsx")):
    # Read in file
    xlsx_df = pd.read_excel(filename, sheet_name="Voters", skiprows=2)

    # Drop unnecessary columns
    xlsx_df.drop(columns=cols_to_drop, inplace=True)

    # Select date of the survey to filter by, then drop the Date column
    xlsx_df = xlsx_df[xlsx_df["Date"] == date_to_filter_on]
    xlsx_df.drop(columns="Date", inplace=True)

    # Use Voter column as index
    xlsx_df = xlsx_df.set_index("Voter", drop=True).reset_index(drop=True)

    # Set NAN values to empty string to avoid Attribute Errors
    xlsx_df = xlsx_df.fillna("")

    # For the open questions, replace carriage return symbol with whitespace to prevent
    # messing up the CSV parsing
    for column in xlsx_df.columns:
        if any([column.startswith(open_q) for open_q in open_questions]):
            for i, _ in xlsx_df[column].iteritems():
                xlsx_df.at[i, column] = xlsx_df.at[i, column].replace("\n", " ")

    # Concatenate dataframes
    df = pd.concat([df, xlsx_df], ignore_index=True)

# Swap empty strings back to NANs and drop rows where all values are NAN
df = df.replace("", np.nan).dropna(how="all")

# Output responses as a CSV file
df.to_csv(processed_data_dir.joinpath("cw22-survey-responses.csv"), index_label="Voter")
