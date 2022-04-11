# Preprocessing Code

This directory contains code/scripts/notebooks that process raw data files from the `./cw22-survey/data/raw` directory and output it to the `./cw22-survey/data/processed` directory, ready to be input into analysis code stored in the `.cw22-survey/code/analysis` directory.

## Scripts

- `extract-mentimeter-question-metadata.py`
  - This script extracts metadata about the survey questions from an `xlsx` file output by Mentimeter and are output to a JSON file.
    These data are present on a sheet called "Session 1" after the survey has been run.
    The data extracted are:
    - The question itself,
    - The number of the question as it appeared in the survey,
    - The type of question; e.g., open, rank, scale, etc.,
    - The options respondents could choose between, if the question was not an open one.
- `convert-and-combine-mentimeter-xlsx-files.py`
  - This script converts the survey responses collected in the "Voters" sheet of a Mentimeter `xlsx` output file into a CSV file.
    If multiple `xlsx` files are found, the results are combined into a single CSV.
