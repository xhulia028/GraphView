import os
from enum import Enum
import numpy as np
import matplotlib.pyplot as plt
from graph_utils import PlotInfo, find_yaml, sort_criteria, read_slurm, map_folders_to_colors

class PlotType(Enum):
    BOX_PLOT = 1
    VIOLIN_PLOT = 2


def sort_data(data):
    for folder in data.values():
        combined = list(zip(folder['value'], folder['time']))

        combined.sort(key=lambda x: x[0])
        folder['value'], folder['time'] = zip(*combined)

    for folder in data.values():
        folder['value'] = list(folder['value'])
        folder['time'] = [list(times) for times in folder['time']]

def format_folder_name(folder_name):
    if "fastParticleBuffer" in folder_name:
        suffix = folder_name.replace("fastParticleBuffer", "")

        if suffix.startswith("0") and len(suffix) > 1:
            suffix = f"{suffix[0]}.{suffix[1:]}"

        formatted_percentage = f"{suffix}%"
        return f"fastParticleBuffer {formatted_percentage}"
    return folder_name


def darken_color(color, factor=0.6):
    rgb = np.array(color[:3], dtype=np.float64)
    darker_rgb = np.clip(rgb * factor, 0, 1)
    return tuple(darker_rgb) + (color[3],)

def plot_grouped_boxplots(ax, x, y, width, folder, color):
    bp = ax.boxplot(
        y,
        positions=x,
        widths=width,
        patch_artist=True,
        manage_ticks=False,
        showmeans=True,
        meanprops={
            "marker": "o",
            "markerfacecolor": "red",
            "markeredgecolor": "black",
            "markersize": 5,
        },
    )

    for box in bp['boxes']:
        box.set(facecolor=color, alpha=0.7)
    for median in bp['medians']:
        median.set(color='blue', linewidth=1.5)
    for mean in bp['means']:
        mean.set(color='red', linewidth=1.5, linestyle='--')

    ax.scatter([], [], color=color, label=format_folder_name(folder))

def plot_grouped_violinplots(ax, x, y, width, folder, color):
    parts = ax.violinplot(
        y,
        positions=x,
        showmeans=True,
        showextrema=True,
        showmedians=True,
        widths=width
    )

    parts['cmedians'].set_linestyle('--')

    for body in parts['bodies']:
        body.set_facecolor(color)
        body.set_edgecolor('black')
        body.set_alpha(0.6)

    for part_name in ('cmeans', 'cmedians', 'cmaxes', 'cmins', 'cbars'):
        if part_name in parts:
            parts[part_name].set_edgecolor(darken_color(color))

    ax.scatter([], [], color=color, label=format_folder_name(folder))

def plot(data, folders, title, plot_type=PlotType.BOX_PLOT):
    sort_data(data)
    folders = sorted(folders, key=sort_criteria)
    folder_colors = map_folders_to_colors(folders)

    fig_width = 15  # Width of the figure in inches
    fig, ax = plt.subplots(figsize=(fig_width, 9))

    original_positions = list(data[list(data.keys())[0]]["value"])
    num_positions = len(original_positions)
    num_folders = len(folders)

    boxplot_width = fig_width / num_positions
    width = boxplot_width / (num_folders * 1.5)
    offset = width * 1.5
    group_spacing = boxplot_width * 1.2

    ticks = [pos * group_spacing for pos in range(num_positions)]

    for i, folder in enumerate(folders):
        adjusted_positions = [
            tick - (num_folders - 1) * offset / 2 + i * offset for tick in ticks
        ]

        y = data[folder]["time"]
        color = folder_colors[folder]

        if plot_type == PlotType.BOX_PLOT:
            plot_grouped_boxplots(ax, adjusted_positions, y, width, folder, color)
        elif plot_type == PlotType.VIOLIN_PLOT:
            plot_grouped_violinplots(ax, adjusted_positions, y, width, folder, color)
        else:
            raise ValueError(f'No such plot type as "{plot_type}"')


    for x in ticks[:-1]:
        ax.axvline(x + group_spacing / 2, color="gray", linestyle="--", alpha=0.5)

    ax.set_xticks(ticks)
    ax.set_xticklabels(original_positions, fontsize=12, rotation=45)

    ax.set_title(title, fontsize=16)
    ax.set_xlabel("Frequency", fontsize=14)
    ax.set_ylabel("Time (s)", fontsize=14)
    ax.legend(title="Buffer Thresholds", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.show()

def plot_distribution_graph(base_path, plot_type: PlotType, folders=[]):
    if not "Percentage" in base_path:
        print("This plot can only be used with percentage experiments. Try another plot!")
        return

    if len(folders) == 0:
        folders = [name for name in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, name))]

    yaml_file_name, yaml_file_path = find_yaml(base_path)

    title = "Frequency" if "frequency" in base_path else "Iteration"
    title = title + f" in {yaml_file_name}"

    data = read_slurm( folders, base_path, True, True)
    plot(data, folders, title, plot_type)


if __name__ == "__main__":
    base_path = ""
    folders = []

    plot_distribution_graph(base_path, PlotType.VIOLIN_PLOT, folders)


