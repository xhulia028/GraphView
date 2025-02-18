from graph_utils import PlotInfo, get_plotting_data, get_iterations, get_frequencies


def calculate_folderwise_averages_and_sums(base_path, folder_names, value, column_names, avg_window):
    mode = 0 if "frequency" in base_path else 1
    folder_stats = {}

    for folder_name in folder_names:
        try:
            data = get_plotting_data(base_path, folder_name, value, column_names, mode, avg_window)
            if data is not None and not data.empty:
                averages = {col: data[col].mean() for col in column_names}
                sums_ns = {col: data[col].sum() for col in column_names}  # Sum in nanoseconds
                sums_s = {col: data[col].sum() / 1e9 for col in column_names}  # Convert ns to s

                folder_stats[folder_name] = {
                    "Averages": averages,
                    "Sums (ns)": sums_ns,
                    "Sums (s)": sums_s,
                }
            else:
                folder_stats[folder_name] = {
                    "Averages": {col: None for col in column_names},
                    "Sums (ns)": {col: None for col in column_names},
                    "Sums (s)": {col: None for col in column_names},
                }
        except Exception as e:
            print(f"Error processing folder {folder_name}: {e}")
            folder_stats[folder_name] = {
                "Averages": {col: None for col in column_names},
                "Sums (ns)": {col: None for col in column_names},
                "Sums (s)": {col: None for col in column_names},
            }

    # Print the results
    print("Folder Statistics:")
    for folder, stats in folder_stats.items():
        print(f"\nFolder: {folder}")
        print("  Averages:")
        for col, avg in stats["Averages"].items():
            print(f"    {col}: {avg}")
        print("  Sums:")
        for col in column_names:
            print(f"    {col}: {stats['Sums (ns)'][col]} ns | {stats['Sums (s)'][col]} s")

    return folder_stats  # Returning the dictionary for further use

def compute_pairwise_differences(folder_stats):
    # Get all folder names
    folder_names = list(folder_stats.keys())

    if len(folder_names) < 2:
        print("At least two folders are required for pairwise comparison.")
        return None

    # Initialize total absolute difference sum
    total_difference = 0

    # Get column names from the first folder's averages
    column_names = list(folder_stats[folder_names[0]]["Averages"].keys())

    print("Pairwise Differences:")
    for i in range(len(folder_names) - 1):
        folder1, folder2 = folder_names[i], folder_names[i + 1]
        print(f"\nSubtracting values of {folder1} FROM {folder2}")

        for col in column_names:
            avg1, avg2 = folder_stats[folder1]["Averages"][col], folder_stats[folder2]["Averages"][col]
            sum_ns1, sum_ns2 = folder_stats[folder1]["Sums (ns)"][col], folder_stats[folder2]["Sums (ns)"][col]
            sum_s1, sum_s2 = folder_stats[folder1]["Sums (s)"][col], folder_stats[folder2]["Sums (s)"][col]

            if avg1 is not None and avg2 is not None:
                diff_avg = avg2 - avg1
                diff_sum_ns = sum_ns2 - sum_ns1
                diff_sum_s = sum_s2 - sum_s1

                total_difference += abs(diff_avg)

                print(f"  {col}:")
                print(f"    Averages: {folder2} - {folder1} = {diff_avg}")
                print(f"    Sums (ns): {folder2} - {folder1} = {diff_sum_ns} ns")
                print(f"    Sums (s): {folder2} - {folder1} = {diff_sum_s} s")
            else:
                print(f"  {col}: Cannot compute (missing values)")

    print(f"\nTotal Absolute Difference Sum (for Averages): {total_difference}")
    return total_difference


if __name__ == "__main__":

    base_path = "/home/xhulia/Desktop/Experiments/PercentageExperiments/spinodialDecomposition_equilibration_normal_temp/vlc_c08/frequency_tests"
    avg_window = 1
    value = 20
    columns = [ 'computeInteractions[ns]', 'remainderTraversal[ns]', 'rebuildNeighborLists[ns]']
    folders = ["fastParticleBuffer5", "dynamicVLMerge"]

    data = calculate_folderwise_averages_and_sums(base_path, folders, value , columns, avg_window)


