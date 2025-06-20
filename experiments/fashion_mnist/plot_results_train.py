import os
import pandas as pd
import matplotlib.pyplot as plt
import re

# Path to folder containing CSV files
folder_path = "output_metrics/experiment_0_ 1734726_107304309"

# Data structure: {dt_value: [DataFrames]}
dt_to_dfs = {}

# Step 1: Read and group CSVs by DT value
# Regular expression to extract DT value from filename
dt_pattern = re.compile(r'DT\s*=\s*(\d*\.?\d+(?:[eE][-+]?\d+)?)')

for filename in sorted(os.listdir(folder_path)):
    if "Test DT =" not in filename:
        continue

    filepath = os.path.join(folder_path, filename)

    match = dt_pattern.search(filename)
    if not match:
        print(f"Skipping: {filename} (no DT match)")
        continue

    try:
        dt = float(match.group(1))
    except ValueError:
        print(f"Invalid DT in filename: {filename}")
        continue

    try:
        df = pd.read_csv(filepath, encoding='utf-8')
    except Exception as e:
        print(f"Failed to read {filename}: {e}")
        continue

    if dt not in dt_to_dfs:
        dt_to_dfs[dt] = []
    dt_to_dfs[dt].append(df)

# Step 2: Average across experiments per DT
def calculate_average_across_experiments(grouped_results):
    average_results = {}

    for dt_value, df_list in grouped_results.items():
        concatenated_df = pd.concat(df_list, axis=0)
        averaged_df = concatenated_df.groupby('Epochs').mean().reset_index()
        average_results[dt_value] = averaged_df

    return average_results


# Step 3: Plot metrics over epochs for each DT
def plot_metrics_across_dt(average_results, selected_metrics=None, start_epoch=1):
    """
    Plot selected metrics over epochs for each DT value.

    Parameters:
    - average_results: dict of {DT: DataFrame}
    - selected_metrics: list of column names to plot
    - start_epoch: int, epoch number from which to start plotting (inclusive)
    """
    example_df = next(iter(average_results.values()))
    metrics = [col for col in example_df.columns if col != 'Epochs']

    if selected_metrics:
        metrics = [m for m in metrics if m in selected_metrics]

    for metric in metrics:
        plt.figure(figsize=(10, 6))
        for dt_value, avg_df in sorted(average_results.items()):
            # Filter from start_epoch onward
            filtered_df = avg_df[avg_df['Epochs'] >= start_epoch]
            print(filtered_df)
            plt.plot(filtered_df['Epochs'], filtered_df[metric], label=f'DT = {dt_value:.4g}')
        plt.grid(True)
        plt.xlabel('Epochs')
        plt.ylabel(metric)
        plt.title(f'{metric} Across Epochs for Different DT values (from epoch {start_epoch})')
        plt.legend()
        plt.tight_layout()
        plt.show()


import matplotlib.pyplot as plt
import pandas as pd

def plot_metric_rank_across_dt(average_results, metric='Accuracy (%)', start_epoch=1):
    """
    Plot rank of a selected metric over epochs for each DT value, with markers for clarity.

    Parameters:
    - average_results: dict of {DT: DataFrame}
    - metric: str, the column name to rank
    - start_epoch: int, epoch number from which to start plotting (inclusive)
    """
    # Merge all dataframes on Epochs
    merged_df = pd.DataFrame()
    for dt, df in average_results.items():
        filtered_df = df[df['Epochs'] >= start_epoch].copy()
        filtered_df = filtered_df[['Epochs', metric]].copy()
        filtered_df = filtered_df.rename(columns={metric: f'{dt:.6f}'})
        if merged_df.empty:
            merged_df['Epochs'] = filtered_df['Epochs'].reset_index(drop=True)
        merged_df = pd.concat([merged_df.reset_index(drop=True), filtered_df.drop(columns='Epochs').reset_index(drop=True)], axis=1)

    # Set Epochs as index to rank row-wise (each epoch)
    merged_df.set_index('Epochs', inplace=True)

    # Compute ranks: lower rank is better (rank 1 is best)
    rank_df = merged_df.rank(axis=1, method='min', ascending=False)

    # Plot with markers
    plt.figure(figsize=(10, 6))
    markers = ['o', 's', '^', 'D', 'v', '*', 'P', 'X', 'h', '8']
    for i, dt in enumerate(rank_df.columns):
        marker = markers[i % len(markers)]
        plt.plot(rank_df.index, rank_df[dt], label=f'DT = {dt}', marker=marker)

    plt.gca().invert_yaxis()  # Rank 1 on top
    plt.grid(True)
    plt.xlabel('Epochs')
    plt.ylabel(f'Rank of {metric}')
    plt.title(f'Rank of {metric} Across Epochs for Different DT values (from epoch {start_epoch})')
    plt.legend()
    plt.tight_layout()
    plt.show()


def scatter_plot_spike_times(input_spike_times, spike_times, output_spikes_times, discrete_output_spike_times, label, DT, timestep, PLOT_DIR):
    fig, (ax0, ax1, ax2) = plt.subplots(3, 1, figsize=(10, 15))

    for neuron_index in range(input_spike_times.shape[0]):
        # Plot spike times for the current neuron with a specific color
        ax0.scatter(input_spike_times[neuron_index], [neuron_index] * input_spike_times.shape[1], label=f'Neuron {neuron_index}')
    ax0.set_xlabel('Spike Times (s)')
    ax0.set_ylabel('Neuron Index')
    ax0.set_title('Scatter Plot of Input Layer Spike Times for Each Neuron')

    plt.subplots_adjust(hspace=0.4)

    for neuron_index in range(spike_times.shape[0]):
        # Plot spike times for the current neuron with a specific color
        ax1.scatter(spike_times[neuron_index], [neuron_index] * spike_times.shape[1], label=f'Neuron {neuron_index}')
    ax1.set_xlabel('Spike Times (s)')
    ax1.set_ylabel('Neuron Index')
    ax1.set_title('Scatter Plot of Hidden Layer Spike Times for Each Neuron')

    for neuron_index in range(discrete_output_spike_times.shape[0]):
        # Plot spike times for the current neuron with a specific color
        ax2.scatter(discrete_output_spike_times[neuron_index], [neuron_index] * discrete_output_spike_times.shape[1],
                    label=f'Neuron {neuron_index}', color='b')

    for neuron_index in range(output_spikes_times.shape[0]):
        # Plot spike times for the current neuron with a specific color
        ax2.scatter(output_spikes_times[neuron_index], [neuron_index] * output_spikes_times.shape[1],
                    label=f'Neuron {neuron_index}', color='r')

    ax2.set_xlabel('Spike Times (s)')
    ax2.set_ylabel('Neuron Index')
    ax2.set_title('Scatter Plot of Output Layer Spike Times for Each Neuron')
    ax2.hlines(label, 0, 0.2, color='r', linestyles='dashed', label=f'True Label')
    plt.subplots_adjust(hspace=0.4)

    plt.savefig( PLOT_DIR / ('spike_times_plot_' + str(timestep) + ".png"))
    plt.show()

def plot_heatmap(weights, title="Weight Heatmap"):
    plt.figure(figsize=(10, 8))
    plt.imshow(weights, aspect='auto', cmap='viridis')
    plt.colorbar()
    plt.title(title)
    plt.xlabel('Input Neurons')
    plt.ylabel('Output Neurons')
    plt.show()

# def calculate_latency_prob(discrete_out_spikes: cp.ndarray, labels):
#     # This is for latency
#     batch_size, num_neurons, time_steps = discrete_out_spikes.shape
#     # Convert LATENCY_TIMES_LIST to a CuPy array for efficient broadcasting
#     latency_times_array = cp.array(LATENCY_TIMES_LIST)
#     # Create a dictionary to store the results
#     probabilities_list = {latency: [] for latency in LATENCY_TIMES_LIST}
#     # Get the labels as a CuPy array
#     # Extract spikes for the target neurons based on labels
#     target_spikes = cp.array([discrete_out_spikes[i, labels[i], :] for i in range(batch_size)])
#     # Loop over each latency time
#     for latency in latency_times_array:
#         # Create a mask for spikes that occur before the given latency time
#         latency_mask = target_spikes <= latency
#         # print(latency_mask)
#         # Count the spikes for each batch and latency time
#         count_spikes = cp.sum(latency_mask, axis=1)
#         # print(count_spikes)
#         # Calculate probabilities and store in the list
#         probabilities_list[latency.item()] = (count_spikes / TARGET_TRUE).tolist()
#     return probabilities_list


# Step 4: Execute
average_results = calculate_average_across_experiments(dt_to_dfs)
#
# plot_metric_rank_across_dt(
#     average_results,
#     metric='Accuracy (%)',
#     start_epoch=0
# )


plot_metrics_across_dt(
    average_results,
    selected_metrics=['Accuracy (%)', 'Hidden layer 1 spike counts'],
    start_epoch=10
)







