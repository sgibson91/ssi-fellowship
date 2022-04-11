import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def process_and_combine_responses(output_file, survey_date=None):
    """Combine xlsx files from the ./cw22-survey/data/raw folder containing Mentimeter
    survey responses into a single CSV file for analysis.

    Args:
        output_file (str): The name of the file to save processed survey responses in.
        survey_date (str, optional): The date the desired responses were collected, if
            the survey was run more than once. Defaults to None.
    """
    # Set directory paths
    ABSOLUTE_HERE = Path(__file__).parent
    raw_data_dir = ABSOLUTE_HERE.parent.parent.joinpath("data/raw")
    processed_data_dir = ABSOLUTE_HERE.parent.parent.joinpath("data/processed")

    # Columns not required for analysis
    columns_to_drop = ["Session", "How to join this survey:", "Thank You!:"]

    # Columns that contain free text responses
    open_questions = [
        "If you publish code",
        "If you don't publish code",
        "Which environment management tools",
        "Which tools",
    ]

    # Empty dataframe to combine responses into
    df = pd.DataFrame({})

    # Find raw xlsx files
    for filename in raw_data_dir.glob("*.xlsx"):
        # Read in file
        xlsx_df = pd.read_excel(filename, sheet_name="Voters", skiprows=2)

        # Drop unnecessary columns
        xlsx_df.drop(columns=columns_to_drop, inplace=True)

        if survey_date is not None:
            xlsx_df = xlsx_df[xlsx_df["Date"] == survey_date]
        xlsx_df.drop(columns="Date", inplace=True)

        # Use Voter column as index
        xlsx_df = xlsx_df.set_index("Voter", drop=True).reset_index(drop=True)

        # Set NAN values to empty string to avoid Attribute Errors
        xlsx_df = xlsx_df.fillna("")

        # For the open questions, replace carriage return symbol with whitespace to
        # prevent messing up the CSV parsing
        for column in xlsx_df.columns:
            if any([column.startswith(open_q) for open_q in open_questions]):
                for i, _ in xlsx_df[column].iteritems():
                    xlsx_df.at[i, column] = xlsx_df.at[i, column].replace("\n", " ")

        # Concatenate dataframes
        df = pd.concat([df, xlsx_df], ignore_index=True)

    # Swap empty strings back to NANs and drop rows where all values are NAN
    df = df.replace("", np.nan).dropna(how="all")

    # Output responses as a CSV file
    df.to_csv(processed_data_dir.joinpath(output_file), index_label="Voter")


def main():
    parser = argparse.ArgumentParser(
        description="Combine a number of Mentimeter output files (xlsx) into a single CSV"
    )

    parser.add_argument(
        "-d",
        "--survey-date",
        type=str,
        default=None,
        help="The date responses were collected on in the format YYYY-MM-DD",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="survey-responses.csv",
        help="""
            The name of the file to save processed survey responses in.
            Default: survey-responses.csv
        """,
    )

    args = parser.parse_args()

    process_and_combine_responses(
        survey_date=args.survey_date,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
