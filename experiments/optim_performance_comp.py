import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

file_path = "../results/optimization_performance/report.csv"
# Load the data
# Check if the file exists and is not empty
if not os.path.exists(file_path):
    print(f"Error: File not found: {file_path}. Optimization results need to be generated first using the Makefile.")
    sys.exit(1)
if os.stat(file_path).st_size == 0:
    print(f"Error: File is empty: {file_path}. Optimization results need to be generated first using the Makefile.")
    sys.exit(1)

# Load the data
try:
    df = pd.read_csv(file_path)
except Exception as e:
    print(f"Error reading CSV: {e}")
    sys.exit(1)
    
df.columns = df.columns.str.strip()
# Define the sample sizes
samples = [6, 12, 18, 24, 50, 100, 200]
last_row = df.tail(1)
# Helper function to extract the values for a method prefix
def get_values(prefix):
    return [int(last_row[f"{prefix}-{s}"].dropna().values[0]) for s in samples]

# Construct the result dictionary
data = {
    "Samples": samples,
    "DEHB": get_values("DEHB"),
    "LITE": get_values("LITE"),
    "LINE": get_values("LINE"),
    "RANDOM": get_values("RANDOM")
}

# Convert to a DataFrame if needed
df = pd.DataFrame(data)

# Plot settings
plt.figure(figsize=(7, 5))
markers = ['o', 's', 'D', '^', 'v']
colors = ['royalblue', 'firebrick', 'gold', 'forestgreen', 'darkorange']
labels = df.columns[1:]
font_size = 14
linestyles = ['-', '--', '-.', ':', (0, (3, 1, 1, 1))]
# Plot each line
# Plot each line with updated fonts and styles
for idx, label in enumerate(labels):
    plt.plot(df["Samples"], df[label], 
             marker=markers[idx], 
             linestyle=linestyles[idx], 
             color=colors[idx], 
             label=label, 
             linewidth=2.5, 
             markersize=7)
    
# Set axis labels and ticks with larger font
tick_values = [6, 12, 24, 50, 100, 200]
plt.xscale("log")
plt.xticks(tick_values, labels=[str(v) for v in tick_values], fontsize=font_size)
plt.xlabel("Samples", fontsize=font_size)
plt.ylabel("% Best", fontsize=font_size)
plt.ylim(25, 105)
y_tick_values = list(range(30, 110, 10))
plt.yticks(y_tick_values, [f"{i}%" for i in y_tick_values], fontsize=font_size)
plt.xticks(fontsize=font_size)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='lower right', fontsize=font_size)
plt.tight_layout()

# Save final version for publication
final_plot_path = "../results/optimization_performance/optimization_performance_comparison.png"
plt.savefig(final_plot_path, dpi=300)
plt.show()
