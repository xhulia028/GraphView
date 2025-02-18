import os
from functools import partial
from graph_utils import PlotInfo, find_yaml, print_yaml_file
from runtime_graph import plot_runtime, PlotType as PlotTypeRuntime
from csv_analyzer_graph import PlotType as PlotTypeCSV, CsvAnalyzer
from distribution_graph import plot_distribution_graph, PlotType as PlotTypeDistribution

folders = ["fastParticleBuffer", "dynamicVLMerge"]

# Time vs Frequency or vs Iterations
def runtime(base_path):
    ### plot_runtime will by default plot all folders in path, which sometimes is not ideal
    # it takes a folders param, which is recommended to be set depending on what experiment you are running

    folders_percentages = ["fastParticleBuffer10", "fastParticleBuffer15", "fastParticleBuffer20", "fastParticleBuffer30", "dynamicVLMerge"]

    plot_runtime(base_path, PlotTypeRuntime.SCATTER_PLOT, folders)

# Compare Compute Interactions in DVL and FP
# Compare Remainder Traversal in DVL and FP
def compare_dvl_fp(base_path):
    col = ['computeInteractions[ns]', 'rebuildNeighborLists[ns]']
    columns = ['Iteration', col[0], 'remainderTraversal[ns]']
    plot_info = PlotInfo('Iteration', 'Time [ns]', 'Graph')
    cvs_anal = CsvAnalyzer(base_path, columns, plot_info, PlotTypeCSV.DOUBLE_PLOT, 100, folders)
    cvs_anal.create_window()

# Number of Particles in Buffer vs in Container in FastParticleBuffer
def buffer_vs_container(base_path):
    #numberFastParticles
    columns = ['Iteration', 'particleBufferSize', 'numberOfParticlesInContainer']
    plot_info = PlotInfo('Iteration', 'Number of Particles in Buffer', 'Graph')
    cvs_anal = CsvAnalyzer(base_path, columns, plot_info, PlotTypeCSV.SINGLE_PLOT, 1, ["fastParticleBuffer"])
    cvs_anal.create_window()

def fast_particles(base_path):
    #numberFastParticles
    columns = ['Iteration', 'numberFastParticles']
    plot_info = PlotInfo('Iteration', 'particleBufferSize', 'Graph')
    cvs_anal = CsvAnalyzer(base_path, columns, plot_info, PlotTypeCSV.SINGLE_PLOT, 1, ["fastParticleBuffer"])
    cvs_anal.create_window()

# Compute Interactions vs Remainder Traversal in Fast Particle Buffer
# avg_window -> the grouping of iterations in the csv file, to take the average from
def ci_vs_rt_fp(base_path):
    columns = ['Iteration', 'remainderTraversal[ns]', 'computeInteractions[ns]']
    plot_info = PlotInfo('Iteration', 'Time [ns]', 'Graph')

    cvs_anal = CsvAnalyzer(base_path, columns, plot_info, PlotTypeCSV.SINGLE_PLOT, 100, folders)
    cvs_anal.create_window()

# Distribution Plots for repeated percentage experiments
# Includes Violin and Box plots
def distribution_plots(base_path, plot_type: PlotTypeDistribution):
    folders = ["fastParticleBuffer0", "fastParticleBuffer01", "fastParticleBuffer001", "fastParticleBuffer0001",
                     "fastParticleBuffer1", "fastParticleBuffer5", "fastParticleBuffer05", "dynamicVLMerge"]
    plot_distribution_graph(base_path, plot_type, folders)

if __name__ == "__main__":



    base_path = os.getcwd()

    yaml_file_name, yaml_file_path = find_yaml(base_path)


    plots = [
        ("Runtime throughout iterations or frequencies", lambda: runtime(base_path)),
        ("Compare Dynamic VL Merge and Fast Particle Buffer", lambda: compare_dvl_fp(base_path)),
        ("Compute Interactions vd Remainder Traversal in Fast Particle Buffer", lambda: ci_vs_rt_fp(base_path)),
        ("Number of Particles in Buffer vs in Container in FastParticleBuffer", lambda: buffer_vs_container(base_path)),
        ("Number of Fast Particles found every Iteration in FastParticleBuffer", lambda: fast_particles(base_path)),
        ("Distribution Plots for repeated percentage experiments (Box)",
         lambda: distribution_plots(base_path, PlotTypeDistribution.BOX_PLOT))
    ]


    # You can try wrapping the following code in a while loop.
    # However, tkinter requires the usage of the main thread, hence it can be buggy or even lead to failure

    print("\nAvailable values:")
    for idx, (plot_name, _) in enumerate(plots):
        print(f"{idx}: {plot_name}")
    user_input = input("Pick an index (or 'q' to quit): ")
    if user_input.lower() == 'q':
        print("Exiting...")

    try:
        choice_idx = int(user_input)
        chosen_plot_function = plots[choice_idx][1]

        print("\n\n===========================================================================")
        print(f"path: {base_path}")
        print("===========================================================================\n\n\n")

        print_yaml_file(yaml_file_path)

        chosen_plot_function()
    except (ValueError, IndexError):
        print("Invalid choice, please try again.")






