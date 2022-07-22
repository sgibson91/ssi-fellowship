import json
import os
import warnings
from itertools import cycle, islice
from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import spacy
from wordcloud import WordCloud

nlp = spacy.load("en_core_web_md")


def generate_colors(df):
    hex_colours = ["#e66581", "#5799c9", "#f5a252", "#9ebd6e", "#e1f0c4"]
    return list(islice(cycle(hex_colours), None, len(df)))


def plot_q1(data, metadata, save_path):
    question = metadata["question"]
    choices = [
        "Other" if "Other - please share in the document" in choice else choice
        for choice in metadata["choices"]
    ]

    hist = data[question].value_counts()

    for choice in choices:
        if choice not in hist.index:
            hist = pd.concat([hist, pd.Series(0, index=[choice])])

    hist.fillna(0, inplace=True)
    hist = hist.reindex(choices)

    plt.figure(figsize=(12, 8))
    ax = hist.plot(kind="bar", color=generate_colors(hist), rot=0)

    ax.set_title(metadata["question"], fontsize=14, y=1.05)
    ax.set_xticklabels([fill(x, 20) for x in choices], fontsize=14)
    ax.set_yticks([])
    ax.bar_label(ax.containers[0], fontsize=14)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    plt.tight_layout()
    plt.savefig(
        save_path.joinpath(f"cw22survey_question{metadata['number']:02}.png"),
        format="png",
        dpi=720,
    )
    plt.close()


def plot_choices(data, metadata, grouping_vars, grouping_col, save_path):
    question = metadata["question"]
    choices = [
        "Other" if "Other - please share in the document" in choice else choice
        for choice in metadata["choices"]
    ]

    fig, axes = plt.subplots(1, len(grouping_vars), figsize=(6 * len(grouping_vars), 4))
    plt.suptitle(question, fontsize=14)

    hist = data[question].value_counts()
    max_y = hist.max()

    for i, group in enumerate(grouping_vars):
        if group != "All":
            hist = data[question][data[grouping_col] == group].value_counts()

        hist.fillna(0, inplace=True)
        hist = hist.reindex(choices)

        for choice in choices:
            if choice not in hist.index:
                hist = pd.concat([hist, pd.Series(data={choice: 0})])

        hist.plot(kind="bar", color=generate_colors(hist), rot=0, ax=axes[i])

        axes[i].set_xticklabels([fill(x, 12) for x in choices], fontsize=8)
        axes[i].set_ylim(0, max_y)
        axes[i].set_yticks([])
        axes[i].set_title(fill(group, 20), fontsize=10, y=1.08)
        axes[i].spines["top"].set_visible(False)
        axes[i].spines["right"].set_visible(False)

        axes[i].bar_label(axes[i].containers[0], padding=8, fontsize=12)

    plt.tight_layout()
    plt.savefig(
        save_path.joinpath(f"cw22survey_question{metadata['number']:02}.png"),
        format="png",
        dpi=720,
    )
    plt.close(fig)


def plot_scales(data, metadata, grouping_vars, grouping_col, save_path):
    question = metadata["question"]
    question_cols = [col for col in data.columns if question in col]
    choices = [
        "Other" if "Other - please share in the document" in choice else choice
        for choice in metadata["choices"]
    ]

    fig, axes = plt.subplots(1, len(grouping_vars), figsize=(6 * len(grouping_vars), 4))
    plt.suptitle(question, fontsize=14)
    y_pos = np.arange(len(choices))

    for i, group in enumerate(grouping_vars):
        new_series = pd.Series(dtype=float)

        if group == "All":
            for j, col in enumerate(question_cols):
                tmp_series = pd.Series(data={choices[j]: data[col].mean()})
                new_series = pd.concat([new_series, tmp_series])
        else:
            for j, col in enumerate(question_cols):
                tmp_series = pd.Series(
                    data={choices[j]: data[col][data[grouping_col] == group].mean()}
                )
                new_series = pd.concat([new_series, tmp_series])

        new_series.fillna(0, inplace=True)

        hbars = axes[i].barh(
            y_pos,
            new_series.sort_values(ascending=True).values,
            color=generate_colors(new_series)[::-1],
        )

        axes[i].set_xlim(0.5, 5.5)
        axes[i].set_xticks([1, 2, 3, 4, 5])
        axes[i].set_xlabel("")
        axes[i].set_yticks([])
        axes[i].set_ylabel("Strongly Disagree", fontsize=12)
        axes[i].set_title(fill(group, 20), fontsize=10, y=1.08)
        axes[i].spines["top"].set_visible(False)

        axes[i].bar_label(hbars, padding=8, fontsize=12)
        axes[i].bar_label(
            hbars,
            labels=new_series.sort_values(ascending=True).index,
            padding=8,
            label_type="center",
            fontsize=12,
        )

        ax2 = axes[i].twinx()
        ax2.set_yticks([])
        ax2.set_ylabel("Strongly Agree", fontsize=12)
        ax2.spines["top"].set_visible(False)

    plt.tight_layout(w_pad=1.5)
    plt.savefig(
        save_path.joinpath(f"cw22survey_question{metadata['number']:02}.png"),
        format="png",
        dpi=720,
    )
    plt.close(fig)


def plot_ranking(data, metadata, grouping_vars, grouping_col, save_path):
    question = metadata["question"]
    question_cols = [col for col in data.columns if question in col]
    column_mapping = {col: col.split(":")[-1].strip() for col in question_cols}
    choices = [
        "Other" if "Other - please share in the document" in choice else choice
        for choice in metadata["choices"]
    ]

    fig, axes = plt.subplots(1, len(grouping_vars), figsize=(6 * len(grouping_vars), 4))
    plt.suptitle(question, fontsize=14)
    y_pos = np.arange(len(choices))

    for i, group in enumerate(grouping_vars):
        if group == "All":
            df = data.loc[:, question_cols]
        else:
            df = data[data[grouping_col] == group].loc[:, question_cols]

        df.rename(columns=column_mapping, inplace=True)
        new_series = pd.Series(dtype=float)

        for col in df.columns:
            tmp_series = pd.Series(data={col: len(choices) - df[col].mean()})
            new_series = pd.concat([new_series, tmp_series])

        for choice in choices:
            if choice not in new_series.index:
                tmp_series = pd.Series(data={choice: 0})
                new_series = pd.concat([new_series, tmp_series])

        new_series.fillna(0, inplace=True)

        hbars = axes[i].barh(
            y_pos,
            new_series.sort_values(ascending=True).values,
            color=generate_colors(new_series)[::-1],
        )

        axes[i].set_xlim(0, len(choices))
        axes[i].set_xticks([])
        axes[i].set_xlabel("")
        axes[i].set_yticks(range(len(choices)))
        axes[i].set_yticklabels(range(1, len(choices) + 1)[::-1], fontsize=8)
        axes[i].set_ylabel("Ranking", fontsize=10)
        axes[i].set_title(fill(group, 20), fontsize=10, y=1.08)
        axes[i].spines["top"].set_visible(False)
        axes[i].spines["right"].set_visible(False)

        axes[i].bar_label(
            hbars,
            labels=[
                fill(lab, 20) for lab in new_series.sort_values(ascending=True).index
            ],
            fontsize=8,
            padding=8,
        )

    plt.tight_layout()
    plt.savefig(
        save_path.joinpath(f"cw22survey_question{metadata['number']:02}.png"),
        format="png",
        dpi=720,
    )
    plt.close(fig)


def plot_open(data, metadata, grouping_vars, grouping_col, save_path):
    question = metadata["question"]
    question_cols = [col for col in data.columns if question in col]

    fig, axes = plt.subplots(1, len(grouping_vars), figsize=(6 * len(grouping_vars), 4))
    plt.suptitle(question, fontsize=14)

    for i, group in enumerate(grouping_vars):
        if group == "All":
            df = data[question_cols]
        else:
            df = data[question_cols][data[grouping_col] == group]

        answer_embs = []
        for j, row in df.iterrows():
            answers = row.dropna().values
            for answer in answers:
                if isinstance(answer, str) and len(answer) > 3:
                    answer_emb = nlp(answer).vector
                    answer_embs.append([j, answer, answer_emb])

        comment_words = " ".join([x[1] for x in answer_embs])

        axes[i].set_title(fill(group, 20), fontsize=10, y=1.08)
        axes[i].axis("off")

        if comment_words:
            wordcloud = WordCloud(
                width=800,
                height=800,
                background_color="white",
                min_font_size=10,
            ).generate(comment_words)
            axes[i].imshow(wordcloud)

    plt.tight_layout()
    plt.savefig(
        save_path.joinpath(f"cw22survey_question{metadata['number']:02}.png"),
        format="png",
        dpi=720,
    )
    plt.close(fig)


# Set filepaths
ABSOLUTE_HERE = Path(os.getcwd()).parent
processed_data_dir = ABSOLUTE_HERE.parent.joinpath("data/processed")
output_dir = ABSOLUTE_HERE.joinpath("outputs")
data_filepath = processed_data_dir.joinpath("survey-responses.csv")
questions_filepath = processed_data_dir.joinpath("questions_metadata.json")

# Load datasets
with open(questions_filepath) as stream:
    question_metadata = json.load(stream)

results = pd.read_csv(data_filepath, index_col="Voter")

# Find grouping column headers
groupings = ["All"] + question_metadata[0]["choices"]

for qmd in question_metadata:
    if qmd["type"] == "choices":
        if qmd["number"] == 1:
            plot_q1(results, qmd, output_dir)
        else:
            plot_choices(
                results, qmd, groupings, question_metadata[0]["question"], output_dir
            )
    elif qmd["type"] == "scales":
        plot_scales(
            results, qmd, groupings, question_metadata[0]["question"], output_dir
        )
    elif qmd["type"] == "ranking":
        plot_ranking(
            results, qmd, groupings, question_metadata[0]["question"], output_dir
        )
    elif qmd["type"] == "open":
        plot_open(results, qmd, groupings, question_metadata[0]["question"], output_dir)
    else:
        warnings.warn(f"Unknown Question Type: Skipping question {qmd['number']}")
