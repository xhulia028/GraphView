import matplotlib
matplotlib.use('TkAgg')
from enum import Enum
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from graph_utils import get_plotting_data, get_iterations, get_frequencies


fig = None
canvas = None
toolbar = None


class PlotType(Enum):
    # one column in one plot for 2 branches and one in another plot for the 2 branches
    DOUBLE_PLOT = 1
    # one plot for one branch
    SINGLE_PLOT = 2

class PlotInfo:
    def __init__(self, x_label, y_label, title ):
        self.x_label = x_label
        self.y_label = y_label
        self.title = title

class CsvAnalyzer:

    def __init__(self, base_path, columns, plot_info: PlotInfo, plot_type: PlotType, avg_window):
        self.base_path = base_path
        self.columns = columns
        self.avg_window = avg_window

        self.plot_info = plot_info
        self.folders = ["fastParticleBuffer", "dynamicVLMerge"]
        self.plot_type = plot_type

        self.mode = 0 if "frequency" in base_path else 1

        if self.mode:
            self.values = get_iterations()
        else:
            self.values = get_frequencies()



    def plot_single(self, value):
        global fig, canvas

        # clear figure
        fig.clf()
        fast_particle_data = get_plotting_data(self.base_path, 'fastParticleBuffer', value, self.columns, self.mode, self.avg_window)

        plt.plot(fast_particle_data[self.columns[0]], fast_particle_data[self.columns[1]],
                 label=self.columns[1], color='b')

        plt.plot(fast_particle_data[self.columns[0]], fast_particle_data[self.columns[2]],
                 label=self.columns[2], color="r")
        plt.title(f'Fast Particle Buffer')
        plt.legend()
        plt.grid(True)
        plt.xlabel(self.plot_info.x_label)
        plt.ylabel(self.plot_info.y_label)

        plt.tight_layout()
        canvas.draw()

    def plot_double(self, value):
        global fig, canvas
        fig.clf()

        # columns = ['Iteration', 'computeInteractions[ns]', 'remainderTraversal[ns]']

        fast_particle_data = get_plotting_data(self.base_path, 'fastParticleBuffer', value, self.columns, self.mode, self.avg_window)
        dynamic_vlmerge_data = get_plotting_data(self.base_path, 'dynamicVLMerge', value, self.columns, self.mode, self.avg_window)

        # plt.figure(figsize=(10, 6))

        plt.subplot(2, 1, 1)
        iteration_col = self.columns[0]
        first_col = self.columns[1]
        second_col = self.columns[2]

        plt.plot(fast_particle_data[iteration_col], fast_particle_data[first_col],
                 label="fastParticleBuffer - computeInteractions[ns]", color='tab:blue')
        plt.plot(dynamic_vlmerge_data[iteration_col], dynamic_vlmerge_data[first_col],
                 label="dynamicVLMerge - computeInteractions[ns]", color='tab:orange')
        plt.title(f'{first_col} vs {first_col}')
        plt.legend()
        plt.grid(True)
        plt.xlabel(iteration_col)
        plt.ylabel(self.plot_info.y_label)

        plt.subplot(2, 1, 2)
        plt.plot(fast_particle_data[iteration_col], fast_particle_data[second_col],
                 label="fastParticleBuffer - remainderTraversal[ns]", color='tab:blue')
        plt.plot(dynamic_vlmerge_data[iteration_col], dynamic_vlmerge_data[second_col],
                 label="dynamicVLMerge - remainderTraversal[ns]", color='tab:orange')

        plt.title(f'{second_col} vs {second_col}')
        plt.legend()
        plt.grid(True)
        plt.xlabel(iteration_col)
        plt.ylabel(self.plot_info.y_label)

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

        if "Percentage" in self.base_path:
            print("This plot is not available for percentage experiments, please choose runtime plot or distribution plot")
            return


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

    base_path = "/home/xhulia/Desktop/Experiments/fallingDrop/vlc_c08/frequency_tests"

    folders = ["fastParticleBuffer", "dynamicVLMerge"]
    yamlFileName = "fallingDrop.yaml"



    #def __init__(self, base_path, columns, plot_info: PlotInfo, plot_type: PlotType):
    columns =  ['Iteration', 'particleBufferSize', 'numberOfParticlesInContainer']
    columns2 = ['Iteration', 'remainderTraversal[ns]', 'computeInteractions[ns]']
    plot_info = PlotInfo('Iteration', 'Number of Particles', 'Graph' )
    cvs_anal = CsvAnalyzer(base_path, columns2,plot_info, PlotType.SINGLE_PLOT )
    cvs_anal.create_window()
