import argparse
import json
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook


def extract_question_metadata(input_file, output_file):
    """Function to extract metadata about Mentimeter survey questions from an xlsx file
    and output the metadata as JSON

    Args:
        input_file (str): The input file to extract the metadata file from. Must be an
            xlsx with a sheet called "Session 1".
        output_file (str): The output file to store the extracted metadata in. Must be
            a JSON.
    """
    # Set filepaths
    ABSOLUTE_HERE = Path(__file__).parent
    raw_data_dir = ABSOLUTE_HERE.parent.parent.joinpath("data/raw")
    processed_data_dir = ABSOLUTE_HERE.parent.parent.joinpath("data/processed")
    filename = raw_data_dir.joinpath(input_file)

    # Empty list to store metadata in
    questions_metadata = []

    # Open the Excel file and load the appropriate sheet
    book = load_workbook(filename)
    sheet = book["Session 1"]

    # Loop over the slides that have questions. Number 1 is just a slide with no question.
    for num in range(2, 15):
        # Empty dict to store metadata
        qmd = {}

        # The metadata for each question is preceded by a cell containing the string
        # "Question #". We locate this cell to establish where we should start reading
        # in values from.
        qid = f"Question {num}"

        # Find the cell where the metadata for this question begins
        for cell in sheet["A"]:
            if cell.value == qid:
                # Load in basic info
                question_info = pd.read_excel(
                    filename,
                    sheet_name="Session 1",
                    header=None,
                    index_col=0,
                    usecols="A:B",
                    skiprows=cell.row,
                    nrows=5,
                ).squeeze("columns")

                qmd["number"] = num - 1
                qmd["type"] = question_info["Type"]
                qmd["question"] = question_info["Question"]

                # All question types, except for 'open' have pre-determined choices
                if qmd["type"] != "open":
                    question_choices = pd.read_excel(
                        filename,
                        sheet_name="Session 1",
                        header=None,
                        usecols="A",
                        skiprows=cell.row + 7,
                        nrows=6,
                    ).squeeze("columns")
                    question_choices = question_choices.dropna(how="all")
                    qmd["choices"] = question_choices.values.tolist()

                else:
                    qmd["choices"] = []

                # Add this question's metadata to the list
                questions_metadata.append(qmd)

                # Advance to the next question
                continue

    # Output the metadata to a JSON file
    with open(processed_data_dir.joinpath(output_file), "w") as stream:
        json.dump(questions_metadata, stream)


def main():
    parser = argparse.ArgumentParser(
        description="Extract metadata about survey questions from a Mentimeter output file"
    )

    parser.add_argument(
        "input",
        type=str,
        help="The Mentimeter xlsx file to extract metadata from",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="questions_metadata.json",
        help="The JSON file to store extracted metadata in. Default: questions_metadata.json",
    )

    args = parser.parse_args()

    extract_question_metadata(args.input, args.output)


if __name__ == "__main__":
    main()
