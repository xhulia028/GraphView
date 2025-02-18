import matplotlib
import os
matplotlib.use('TkAgg')
from enum import Enum
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from graph_utils import PlotInfo, get_plotting_data, generate_distinct_colors, extract_sorted_values, map_folders_to_colors


fig = None
canvas = None
toolbar = None


class PlotType(Enum):
    # one column in one plot for 2 branches and one in another plot for the 2 branches
    DOUBLE_PLOT = 1
    # one plot for one branch
    SINGLE_PLOT = 2


class CsvAnalyzer:

    def __init__(self, base_path, columns, plot_info: PlotInfo, plot_type: PlotType, avg_window, folders):

        self.base_path = base_path
        self.columns = columns
        self.avg_window = avg_window

        self.plot_info = plot_info
        if len(folders) < 1:
            raise TypeError("Length of folders is 0. There must at least be one folder")
        self.folders = folders
        print(folders)
        self.plot_type = plot_type

        self.mode = 0 if "frequency" in base_path else 1

        # if self.mode:
        #     self.values = get_iterations()
        # else:
        #     self.values = get_frequencies()

        self.values = extract_sorted_values(os.path.join(base_path, folders[0]))



    def plot_single(self, value):
        global fig, canvas
        fig.clf()  # Clear the figure to start fresh

        len_columns = len(self.columns)
        len_folders = len(self.folders)

        print(self.folders)

        folder_colors = map_folders_to_colors(self.folders)

        random_colors = generate_distinct_colors(len_columns * len_folders)

        color_flag = len_columns < 2 and set(self.folders).issubset(["fastParticleBuffer", "dynamicVLMerge"])

        ax = fig.add_subplot(111)
        counter = 0
        for i in range(0, len_folders):

            folder = self.folders[i]
            data = get_plotting_data(self.base_path, folder, value, self.columns, self.mode,
                                                   self.avg_window)


            for j in range(1, len_columns): #the first column is the iteration column which is basically the x-axis

                color = folder_colors[folder] if color_flag else random_colors[counter]
                ax.plot(data[self.columns[0]], data[self.columns[j]],
                        label=f"{folder} - {self.columns[j]}", color=color)
                counter += 1

        # ax.plot(fast_particle_data[self.columns[0]], fast_particle_data[self.columns[2]],
        #         label=self.columns[2], color="r")

        # ax.set_title('Fast Particle Buffer')
        ax.set_xlabel(self.plot_info.x_label, fontsize=18)
        ax.set_ylabel(self.plot_info.y_label, fontsize=18)
        ax.tick_params(axis='both', which='major', labelsize=16)
        ax.legend(fontsize=14)
        ax.grid(True)

        canvas.draw()

    def plot_double(self, value):
        global fig, canvas
        fig.clf()  # Clear the figure

        len_columns = min(3, len(self.columns))  # Ensure max 2 y-columns + 1 x-column
        len_folders = len(self.folders)

        if len_columns < 2:
            print("Error: Need at least 2 columns (one X and one Y) for plotting.")
            return

        folder_colors = map_folders_to_colors(self.folders)
        random_colors = generate_distinct_colors(len_folders)  # One color per folder

        color_flag = len_folders == 2 and set(self.folders).issubset({"fastParticleBuffer", "dynamicVLMerge"})

        ax1 = plt.subplot(2, 1, 1)
        ax2 = plt.subplot(2, 1, 2)

        for i, folder in enumerate(self.folders):
            data = get_plotting_data(self.base_path, folder, value, self.columns, self.mode, self.avg_window)

            color = folder_colors[folder] if color_flag else random_colors[i]

            ax1.plot(data[self.columns[0]], data[self.columns[1]],
                     label=f"{folder} - {self.columns[1]}", color=color)

            ax2.plot(data[self.columns[0]], data[self.columns[2]],
                     label=f"{folder} - {self.columns[2]}", color=color)

        # Formatting for ax1
        ax1.legend(fontsize=14)
        ax1.grid(True)
        ax1.set_xlabel(self.columns[0], fontsize=18)
        ax1.set_ylabel(self.plot_info.y_label, fontsize=18)
        ax1.tick_params(axis='both', which='major', labelsize=18)
        ax1.ticklabel_format(style='scientific', axis='y', scilimits=(-2, 2))

        # Formatting for ax2
        ax2.legend(fontsize=14)
        ax2.grid(True)
        ax2.set_xlabel(self.columns[0], fontsize=18)
        ax2.set_ylabel(self.plot_info.y_label, fontsize=18)
        ax2.tick_params(axis='both', which='major', labelsize=18)
        ax2.ticklabel_format(style='scientific', axis='y', scilimits=(-2, 2))

        plt.tight_layout()
        canvas.draw()

    def plot(self, value):

        if self.plot_type == PlotType.SINGLE_PLOT:
            self.plot_single(value)
        elif self.plot_type == PlotType.DOUBLE_PLOT:
            self.plot_double(value)
        else:
            raise TypeError(f"No such plot type as: {self.plot_type}")


    def create_window(self):

        # if "Percentage" in self.base_path:
        #     print("This plot is not available for percentage experiments, please choose runtime plot or distribution plot")
        #     return


        global fig, canvas, toolbar

        window = tk.Tk()
        window.resizable(True, True)

        # window.title(self.plot_info[''])

        dropdown_var = tk.StringVar(window)

        dropdown_var.set(str(self.values[0]))
        dropdown = ttk.Combobox(window, textvariable=dropdown_var, values=[str(v) for v in self.values], state='readonly')
        dropdown.bind('<<ComboboxSelected>>', lambda event: self.update_plot(dropdown_var.get()))
        dropdown.pack(side=tk.TOP, pady=10)

        fig = plt.figure(figsize=(15, 9))
        frame = tk.Frame(window)
        frame.pack(fill='both', expand=True, padx=15, pady=15)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

        toolbar = NavigationToolbar2Tk(canvas, window)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.plot(int(dropdown_var.get()))

        window.protocol("WM_DELETE_WINDOW", window.quit)
        window.mainloop()

    def update_plot(self, selected_value):
        global canvas
        selected_value = int(selected_value)
        self.plot(selected_value)

if __name__ == "__main__":

    base_path = ""

    folders = []
    columns =  []
    xlabel = ''
    ylabel = ''
    title = ''
    plot_info = PlotInfo(xlabel, ylabel, title )
    cvs_analyzer = CsvAnalyzer(base_path, columns,plot_info, PlotType.DOUBLE_PLOT, 100, ["fastParticleBuffer1", "fastParticleBuffer5"] )
    cvs_analyzer.create_window()
