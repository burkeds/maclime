"""
Created on May 18, 2022

@author: Devin Burke
"""

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import textwrap
import math
from mhw.read_statistics import get_possible_answers
from mhw.scoring import get_value_dict
from mhw.read_results import get_included_responses
from mhw.scoring import get_scored_data


def make_histo(frame, title, description, complementary=False, save_figure=False, x_labels=None, y_label=None):
    """
    Makes a histogram of the data in the given frame.
    :param frame: The frame to be plotted
    :param title: The title of the plot
    :param description: The description of the plot
    :param complementary: Whether to use the complementary scores
    :param save_figure: Whether to save the figure
    :param x_labels: The labels for the x axis
    :param y_label: The labels for the y axis
    :return:
    """
    plt.clf()
    sample = frame.attrs['sample_size']
    if complementary:
        data = frame.attrs['complementary_scores']
        included_respondents = frame.attrs['complementary_respondents']
        res_str = "(" + str(included_respondents) + " of " + str(sample) + ")"
        description = "(comp)" + description
    else:
        data = frame.attrs['include_scores']
        included_respondents = frame.attrs['included_respondents']
        res_str = "(" + str(included_respondents) + " of " + str(sample) + ")"
    title += res_str
    if not x_labels:
        possible_answers = frame.attrs['possible_answers']
        bad_labels = ['Not applicable', 'No answer', 'Not completed or Not displayed']
        x_labels = [x for x in possible_answers if x not in bad_labels]
    if not y_label:
        y_label = 'Respondent count'

    _, ax = plt.subplots()
    arrays, __, patches = ax.hist(data,
                                  bins=[-2.5, -1.5, -0.5, 0.5, 1.5, 2.5],
                                  edgecolor='black',
                                  linewidth=1, zorder=3)
    ax.bar_label(patches)
    ax.set_title(title + "\n" + description)
    ax.set_xticks([-2, -1, 0, 1, 2])
    ax.set_xticklabels(x_labels)
    ax.grid(axis='y', zorder=0)
    ax.set_ylabel(y_label)
    color = {0: 'red', 1: 'orange', 2: 'yellow', 3: '#90EE90', 4: '#013220'}
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    for i in range(len(arrays)):
        patches[i].set_facecolor(color[i])
    if save_figure:
        plt.savefig(title + "_" + description + ".png")
    plt.show()


def plot_impact_statistics(impact_statistics,
                           complement=False,
                           title="",
                           x_labels=None,
                           y_label=None,
                           include_sample_size=True,
                           save_figure=False):
    """
    Plots the impact statistics for the given question.
    :param impact_statistics: The impact statistics for the question
    :param complement: Whether to plot the complementary statistics
    :param title: The title of the plot
    :param x_labels: The labels for the x-axis
    :param y_label: The label for the y-axis
    :param include_sample_size: Whether to include the sample size in the title
    :param save_figure: Whether to save the figure
    :return:
    """
    plt.clf()
    df = impact_statistics
    code = df.index[0]

    included_respondents = df.attrs['included_respondents']
    sample_size = df.attrs['sample_size']
    description = df.attrs['description']
    include = df.attrs['include']
    mean_df = df['mean']
    moe_df = df['moe']

    if complement:
        included_respondents = df.attrs['complementary_respondents']
        sample_size = df.attrs['sample_size']
        description = "(comp)" + df.attrs['description']
        include = df.attrs['include_comp']
        mean_df = df['comp_mean']
        moe_df = df['comp_moe']

    # Add information about sample size
    if include_sample_size:
        res_str = "(" + str(included_respondents) + " of " + str(sample_size) + ")"
        description = description + res_str

    if include_sample_size:
        # Generate labels if not specified
        if not x_labels:
            x_labels = df.index.tolist()
        if not y_label:
            y_label = get_possible_answers(code)
            bad_labels = ['Not applicable', 'No answer', 'Not completed or Not displayed']
            y_label = [label for label in y_label if label not in bad_labels]
            y_label = ['\n'.join(textwrap.wrap(label, 10)) for label in y_label]

    # Add valid respondents to x_label
    for i, label in enumerate(x_labels):
        question_code = df.index[i]
        responses = get_included_responses(question_code, include)
        scores = get_scored_data(question_code, responses)
        valid = len(scores)
        p_value = df['pvalue'][question_code]
        x_labels[i] += "\n {}".format(valid)
        x_labels[i] += "\n {}".format(round(p_value, 2))

    # Get bar colours from colourmap
    cmap = matplotlib.colormaps['RdYlGn']
    colours = []
    low_y = min(list(get_value_dict(code).values()))
    high_y = max(list(get_value_dict(code).values()))
    for val in mean_df.values.tolist():
        cval = math.fabs(low_y - val)
        cval = cval / (high_y - low_y)
        colours.append(matplotlib.colors.to_hex(cmap(cval)))
    if mean_df.dropna().values.tolist():
        # Create plot axis
        title = title + "\n" + description
        ax = mean_df.plot.bar(color=colours, title=title, yerr=moe_df, capsize=4)
        ax.set_yticks(range(low_y, high_y + 1))
        ax.set_yticklabels(y_label)
        ax.set_xticklabels(x_labels, rotation=45, fontsize=5.5)
        ax.set_ylim([low_y, high_y])
        ax.tick_params(direction='in')
        if save_figure:
            plt.savefig(title + ".png")
        plt.show()


def create_pie_chart(answers, frequencies, title=None, subtitle=None, save_figure=False):
    """
    Create a pie chart with labels, percentages, title, and subtitle.
    :param answers: list of strings
    :param frequencies: list of ints
    :param title: Title string
    :param subtitle: Subtitle string
    :param save_figure: Whether to save the figure
    :return:
    """
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(6, 6))

    # Create the pie chart
    wedges, labels, autopct_text = ax.pie(frequencies, autopct='%1.1f%%', startangle=90)

    # Set aspect ratio to be equal so that pie is drawn as a circle
    ax.axis('equal')

    # Set the title of the chart
    if title:
        ax.set_title(title)

    # Wrap the subtitle text if it exceeds the chart width
    if subtitle:
        wrapped_subtitle = textwrap.fill(subtitle, len(answers) * 10)
        ax.text(0.5, 0.95, wrapped_subtitle, transform=ax.transAxes, ha='center')

    # Create a legend
    ax.legend(wedges, answers, loc="center left", bbox_to_anchor=(0.85, 0.5))

    # Add percentage labels inside each slice
    for i, label in enumerate(autopct_text):
        if frequencies[i] != 0:
            label.set_text(f"{label.get_text()}%")

    # Show the pie char
    if save_figure:
        plt.savefig(title + ".png")
    plt.show()
