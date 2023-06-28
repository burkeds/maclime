"""
Created on May 18, 2022

@author: Devin Burke
"""

import matplotlib.pyplot as plt
import textwrap


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
