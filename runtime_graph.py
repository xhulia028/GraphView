import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
from graph_utils import map_folders_to_colors, find_yaml, read_slurm


def plot(data, folders, title):
    plt.style.use('_mpl-gallery')

    colors = map_folders_to_colors(folders)

    fig, ax = plt.subplots(figsize=(10, 4))

    plotted_points = []
    for folder in folders:
        x = np.array(data[folder]["value"])
        y = np.array(data[folder]["time"])

        stem_container = ax.stem(
            x, y,
            linefmt=colors[folder],
            markerfmt='o',
            basefmt='k-',
            label=folder
        )

        stem_container.markerline.set_marker('o')
        stem_container.markerline.set_markersize(8)
        stem_container.markerline.set_markeredgecolor('black')
        stem_container.markerline.set_markerfacecolor(colors[folder])

        # Dynamically adjust zorder based on y-values
        for xi, yi in zip(x, y):
            ax.plot(
                [xi], [yi],
                marker='o',
                markersize=8,
                markeredgecolor='black',
                markerfacecolor=colors[folder],
                zorder=100 - yi  # Higher y values have lower zorder
            )
            ax.vlines(
                xi, 0, yi,
                colors=colors[folder],
                linewidth=2.5,
                zorder=100 - yi - 1  # Ensure stems are below markers
            )

        stem_container.baseline.set_linewidth(1)
        stem_container.baseline.set_linestyle('--')

        for i in range(len(x)):
            plotted_points.append((x[i], y[i], folder))

    ax.set_ylim(0, max([max(data[folder]["time"]) for folder in folders]) * 1.2)

    num_x_ticks = max(5, int(fig.get_figwidth()))
    ax.xaxis.set_major_locator(MaxNLocator(nbins=num_x_ticks))

    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))

    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.15)
    ax.set(
        title=f"{title}",
        xlabel=f"Frequency",
        ylabel="Time (s)",
    )

    ax.title.set_fontsize(16)
    ax.xaxis.label.set_fontsize(14)
    ax.yaxis.label.set_fontsize(14)
    ax.tick_params(axis='both', labelsize=12)

    ax.legend(fontsize=12)

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

def plot_runtime(base_path, folders = []):
    yaml_file_name, yaml_file_path = find_yaml(base_path)
    title = "Frequency" if "frequency" in base_path else "Iteration"

    title = title + f" in {yaml_file_name}"

    if len(folders) == 0:
        folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

    data = read_slurm( folders, base_path, False, False)

    plot(data, folders, title)


if __name__ == "__main__":
    yamlFileName = "/home/xhulia/Desktop/Experiments/fallingDrop/withTuning/SpinodalDecomposition_equilibrationVlc_c08.yaml"
    base_path = "/home/xhulia/Desktop/Experiments/PercentageExperiments/fallingDrop/vlc_c08/frequency_tests"

    #base_path = "/home/xhulia/Desktop/Experiments/PercentageExperiments/spinodialDecomposition_equilibration/vlc_c08/frequency_tests"

    #base_path = "/home/xhulia/Desktop/Experiments/PercentageExperiments/spinodialDecomposition_equilibration/newDeleteFunction/lc_c08/frequency_tests"

    #base_path = "/home/xhulia/Desktop/Experiments/fallingDrop/vlc_c08/frequency_tests"


    folders_pe_old = ["fastParticleBuffer10", "fastParticleBuffer15", "fastParticleBuffer20", "fastParticleBuffer30", "dynamicVLMerge"]
    folders_pe_new = ["fastParticleBuffer1", "fastParticleBuffer5", "fastParticleBuffer05", "fastParticleBuffer10", "dynamicVLMerge"]
    folders_del_fun = ["fastParticleBuffer10", "fastParticleBufferMarkAsDelete10", "dynamicVLMerge"]
    folders_pe_spin = ["fastParticleBuffer1", "fastParticleBuffer5", "dynamicVLMerge"]
    folders_pe_spin_del = ["fastParticleBuffer5", "dynamicVLMerge"]

    fodlers_extra = ["fastParticleBuffer0", "fastParticleBuffer01", "fastParticleBuffer001", "fastParticleBuffer0001", "dynamicVLMerge"]

    folders = fodlers_extra


    plot_runtime(base_path, folders_pe_old +fodlers_extra)