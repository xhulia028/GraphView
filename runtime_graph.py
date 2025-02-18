import os
from enum import Enum
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
import matplotlib.patches as mpatches
from graph_utils import PlotInfo, map_folders_to_colors, sort_criteria, find_yaml, read_slurm



class PlotType(Enum):
    STEM_PLOT = 1
    SCATTER_PLOT = 2
    BAR_PLOT = 3

def merge_folders(data, folder1, folder2, merged_folder_name):
    if folder1 not in data or folder2 not in data:
        raise KeyError("One or both folders not found in data.")

    values1, times1 = data[folder1]["value"], data[folder1]["time"]
    values2, times2 = data[folder2]["value"], data[folder2]["time"]

    time_dict1 = dict(zip(values1, times1))
    time_dict2 = dict(zip(values2, times2))

    if set(time_dict1.keys()) != set(time_dict2.keys()):
        raise ValueError("The two folders do not contain the same values.")

    merged_values = sorted(time_dict1.keys())  # Keep a sorted order
    merged_times = [time_dict1[val] + time_dict2[val] for val in merged_values]

    data[merged_folder_name] = {"value": merged_values, "time": merged_times}

    del data[folder1]
    del data[folder2]

    return data

def plot_bar(data, folders, plot_info):
    folders = sorted(folders, key=sort_criteria)
    colors = map_folders_to_colors(folders)

    fig, ax = plt.subplots(figsize=(10, 4))

    bar_width = 0.2  # Width of each bar
    num_folders = len(folders)

    all_x_values = sorted(set(val for folder in folders for val in data[folder]["value"]))
    x_positions = {val: i for i, val in enumerate(all_x_values)}

    timeout_detected = False  # Track if any timeouts occur

    for i, folder in enumerate(folders):
        x_values = np.array(data[folder]["value"])
        y_values = np.array(data[folder]["time"])

        x = np.array([x_positions[val] for val in x_values])

        ax.bar(
            x + (i - (num_folders - 1) / 2) * bar_width,  # Adjust x-position for centering
            y_values,
            width=bar_width,
            color=colors[folder],
            label=folder,
        )

    # Check for missing data and add "timeout" bars
    for val, pos in x_positions.items():
        for i, folder in enumerate(folders):
            if val not in data[folder]["value"]:  # If missing
                timeout_detected = True
                ax.bar(
                    pos + (i - (num_folders - 1) / 2) * bar_width,
                    max([max(data[f]["time"]) for f in folders]),  # Approximate max height
                    width=bar_width,
                    color='gray',
                    hatch='//',  # Crosshatch pattern
                )

    # Compute center positions for x-axis labels
    x_tick_positions = [pos for pos in x_positions.values()]
    ax.set_xticks(x_tick_positions)
    ax.set_xticklabels(all_x_values)

    ax.set(
        xlabel=plot_info.x_label,
        ylabel=plot_info.y_label,
    )

    ax.title.set_fontsize(16)
    ax.xaxis.label.set_fontsize(14)
    ax.yaxis.label.set_fontsize(14)
    ax.tick_params(axis='both', labelsize=14)

    # Create a legend entry for 'Timeout' manually
    handles, labels = ax.get_legend_handles_labels()
    if timeout_detected:
        timeout_patch = mpatches.Patch(color='gray', hatch='//', label='Timeout')
        handles.append(timeout_patch)
        labels.append('Timeout')

    # Add legend only if there are folders or timeouts
    if len(folders) > 0 or timeout_detected:
        ax.legend(handles, labels, fontsize=14)

    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    plt.show()

def plot(data, folders, plot_info: PlotInfo, plot_type: PlotType):

    if plot_type == PlotType.BAR_PLOT:
        plot_bar(data, folders, plot_info)
        return

    plt.style.use('_mpl-gallery')

    folders = sorted(folders, key=sort_criteria)
    colors = map_folders_to_colors(folders)

    fig, ax = plt.subplots(figsize=(10, 4))

    plotted_points = []

    for folder in folders:
        x = np.array(data[folder]["value"])
        y = np.array(data[folder]["time"])

        if plot_type == PlotType.STEM_PLOT:
            stem_container = ax.stem(
                x, y,
                linefmt=colors[folder],
                markerfmt='o',
                basefmt='k-',
                label=folder
            )

            stem_container.baseline.set_linewidth(1)
            stem_container.baseline.set_linestyle('--')

        elif plot_type == PlotType.SCATTER_PLOT:
            marker_style = 'o' if "dynamicVLMerge" in folder else '^'

            scatter = ax.scatter(
                x, y,
                marker=marker_style,
                s=80,
                edgecolors=colors[folder],
                facecolors='none',
                linewidth=2
            )

            ax.scatter([], [], marker=marker_style, edgecolors=colors[folder],
                       facecolors='none', s=80, linewidth=1.5, label=folder)

    for xi, yi in zip(x, y):
        plotted_points.append((xi, yi, folder))

    ax.set_ylim(0, max([max(data[folder]["time"]) for folder in folders]) * 1.2)

    num_x_ticks = max(5, int(fig.get_figwidth()))
    ax.xaxis.set_major_locator(MaxNLocator(nbins=num_x_ticks))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))

    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.15)
    ax.set(
        title=plot_info.title,
        xlabel=plot_info.x_label,
        ylabel=plot_info.y_label,
    )

    ax.title.set_fontsize(16)
    ax.xaxis.label.set_fontsize(14)
    ax.yaxis.label.set_fontsize(14)
    ax.tick_params(axis='both', labelsize=14)
    ax.legend(fontsize=14)

    annot = ax.annotate("", xy=(0, 0), xytext=(10, 10),
                        textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(coord, label):
        annot.xy = coord
        text = f"({coord[0]:.2f}, {coord[1]:.2f})"
        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor(colors[label])
        annot.get_bbox_patch().set_alpha(0.8)

    def hover(event):
        if event.inaxes == ax:
            for x, y, label in plotted_points:
                distance = np.sqrt((x - event.xdata) ** 2 + (y - event.ydata) ** 2)
                if distance < 1:
                    update_annot((x, y), label)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return
        annot.set_visible(False)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()


def plot_runtime(base_path, plot_type: PlotType, folders = []):
    yaml_file_name, yaml_file_path = find_yaml(base_path)
    x_label = "Frequency" if "frequency" in base_path else "Iteration"

    title = x_label + " vs Time" + f" in {yaml_file_name}"

    if len(folders) == 0:
        folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

    data = read_slurm( folders, base_path, False, False)

    plot_info = PlotInfo(x_label, "Time(s)", title)

    if folders == ["dynamicVLMerge", "fastParticleBuffer", "fastParticleBuffer_pt1", "fastParticleBuffer_pt2"]:
        data = merge_folders(data, "fastParticleBuffer_pt1", "fastParticleBuffer_pt2", "fastParticleBuffer (two-phase)")
        folders = ["fastParticleBuffer", "fastParticleBuffer (two-phase)", "dynamicVLMerge"]

    plot(data, folders, plot_info, plot_type)



if __name__ == "__main__":

    base_path = ""
    folders = []
    plot_runtime(base_path, PlotType.SCATTER_PLOT, folders)