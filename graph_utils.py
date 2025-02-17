import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
import re
import math
import pandas as pd
import numpy as np
from matplotlib import cm, colors

class PlotInfo:
    def __init__(self, x_label, y_label, title ):
        self.x_label = x_label
        self.y_label = y_label
        self.title = title

def sort_criteria(folder):
    if "fastParticleBuffer" in folder:
        suffix = folder.replace("fastParticleBuffer", "")

        if suffix == '':
            return 100000.0

        if suffix.startswith("0") and len(suffix) > 1:
            suffix = f"{suffix[0]}.{suffix[1:]}"

        try:
            result = float(suffix)

        except ValueError:
            result = 99999

        return result
    else:
        return float('inf')

# supposing the yaml is one level up from path (which is the case most of the time)
def find_yaml(path):
    parent = os.path.dirname(path)
    yaml_files = [f for f in os.listdir(parent) if f.endswith(".yaml")]
    if len(yaml_files) == 0:
        raise Exception(f"No Yaml File was Found in {path}")
    elif len(yaml_files) > 1:
        print("Multiple .yaml Files found. Printing the first one...")

    yaml_file_name= yaml_files[0]
    yaml_file_path = os.path.join(parent, yaml_file_name)

    return yaml_file_name, yaml_file_path


def print_yaml_file(yamlFileNamePath):
    with open(yamlFileNamePath, "r") as yamlFile:
        contents = yamlFile.read()
        print(contents)


def get_iterations():
    iterations = []
    start_iter = 500
    step_size = 500
    runs = 60
    end_iter = start_iter * runs
    iter = start_iter
    while iter <= end_iter:
        iterations.append(iter)
        iter += step_size
    return iterations


def get_frequencies():
    start_freq = 10
    end_freq = 16000
    min_step = 10
    max_step = 200

    def get_step_size(freq):
        log_freq = math.log10(freq)
        step_size = min_step + (log_freq * (max_step - min_step) / math.log10(end_freq))
        return int(step_size)

    frequencies = []
    freq = start_freq
    iteration = 0
    while freq <= end_freq:
        frequencies.append(freq)
        iteration += 1
        step_size = get_step_size(freq)
        freq += step_size
    return frequencies

def map_folders_to_colors(folders):
    blue_cmap_full = cm.get_cmap('Blues')
    blue_cmap = colors.LinearSegmentedColormap.from_list(
        'truncated_Blues', blue_cmap_full(np.linspace(0.3, 1.0, 256))
    )

    fast_particle_folders = [f for f in folders if "fastParticleBuffer" in f]
    num_buffers = len(fast_particle_folders)

    norm = colors.Normalize(vmin=0, vmax=num_buffers - 1)

    folder_colors = {folder: blue_cmap(norm(i)) for i, folder in enumerate(fast_particle_folders)}
    folder_colors["dynamicVLMerge"] = colors.to_rgba('tab:orange')
    folder_colors["fastParticleBuffer"] = colors.to_rgba('tab:blue')
    return folder_colors


def generate_distinct_colors(x):
    cmap = plt.get_cmap("tab10") if x <= 10 else plt.get_cmap("tab20")
    excluded_colors = {cmap(1), cmap(2)}  # tab10: 1 (orange), 2 (blue)

    cols = []
    for i in range(cmap.N):
        color = cmap(i % cmap.N)
        if color not in excluded_colors:
            cols.append(color)
        if len(cols) >= x:
            break

    return cols

def read_slurm(folders, base_path, is_percentage, is_distribution_plot):
    data = {folder: {"value": [], "time": []} for folder in folders}

    time_pattern = re.compile(r"Total wall-clock time\s+:\s+(\d+)\s+ns")

    if "frequency" in base_path:
        pattern = re.compile(r"verlet-rebuild-frequency\s+:\s+(\d+)")
    else:
        pattern = re.compile(r"iterations\s+:\s+(\d+)")

    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        for subfolder in os.listdir(folder_path):
            if "frequency" in subfolder or "iteration" in subfolder:
                subfolder_path = os.path.join(folder_path, subfolder)

                value_pattern = re.compile(r"[a-zA-Z0-9_-]+_(\d+)\.(\d+)")

                files_to_process = os.listdir(subfolder_path)
                oldest_file = None
                slurm_id = float('inf')



                if not is_percentage:
                    for file in os.listdir(subfolder_path):
                        if file.endswith(".out"):
                            match = value_pattern.search(file)

                            if match:
                                d2 = int(match.group(2))  # Extract the second number (d2)
                                if not is_percentage and d2 < slurm_id:
                                    slurm_id = d2
                                    oldest_file = file

                    files_to_process = [oldest_file]



                times = []
                value = -1

                for file in files_to_process:

                    if file.endswith(".out"):
                        file_path = os.path.join(subfolder_path, file)

                        with open(file_path, "r") as f:
                            content = f.read()
                            value_match = pattern.search(content)
                            time_match = time_pattern.search(content)

                            if value_match and time_match:
                                value = int(value_match.group(1))
                                time_ns = int(time_match.group(1))
                                time_s = time_ns / 1e9
                                times.append(time_s)

                                if not is_distribution_plot:
                                    data[folder]["value"].append(value)
                                    data[folder]["time"].append(time_s)

                if is_distribution_plot:
                    data[folder]["value"].append(value)
                    data[folder]["time"].append(times)

    return data


def read_and_process_csv(file_path, column_names, avg_window):
    try:
        df = pd.read_csv(file_path, on_bad_lines='skip')

        # Ensure the relevant columns exist in the dataframe
        if not all(col in df.columns for col in column_names):
            raise ValueError(f"file doesn't contain the following columns: {column_names}")

        num_columns = len(df.columns)  # Number of columns as per header
        df = df[df.notnull().sum(axis=1) == num_columns]

        #remove invalid values
        df[column_names] = df[column_names].apply(pd.to_numeric, errors='coerce')
        df = df.dropna(subset=column_names)
        df[column_names] = df[column_names].astype('int64')
        # df = df[df['Iteration'] < 15000]

        #drop duplicates and sort
        df = df.drop_duplicates(subset=['Iteration'])
        df = df.sort_values(by='Iteration')
        df.reset_index(drop=True, inplace=True)

        # get average of every 10 iterations
        df = df[column_names].groupby(df.index // avg_window).mean()
        df.reset_index(drop=True, inplace=True)


        return df

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None


def get_newest_csv(folder_path):
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    if not csv_files:
        return None

    csv_files_full_path = [os.path.join(folder_path, f) for f in csv_files]

    newest_csv = max(csv_files_full_path, key=os.path.getmtime)

    return newest_csv

def get_plotting_data(base_path, folder_name, value, column_names, mode, avg_window):
    name = "frequency" if mode == 0 else "iteration"
    folder_path = os.path.join(base_path, folder_name, f'{name}_{value}')
    file = get_newest_csv(folder_path)
    if file is None:
        raise TypeError(f'No .csv file in {folder_path}')

    data = read_and_process_csv(file, column_names, avg_window)
    if data is None:
        raise TypeError(f'Data in {folder_path} is none')

    return data



def extract_sorted_values(base_path):
    values = []
    pattern = re.compile(r'_(\d+)$')

    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            match = pattern.search(folder_name)
            if match:
                values.append(int(match.group(1)))

    return sorted(values)


