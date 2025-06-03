import pandas as pd
import matplotlib.pyplot as plt
import re
import os
import sys

# File path
file_path = "../results/optimization_performance/report_tmp.csv"

# Check file existence
if not os.path.exists(file_path):
    print(f"Error: File not found: {file_path}. Optimization results need to be generated first using the Makefile.")
    sys.exit(1)

# Check if file is empty
if os.stat(file_path).st_size == 0:
    print(f"Error: File is empty: {file_path}. Optimization results need to be generated first using the Makefile.")
    sys.exit(1)

# Load the data
try:
    df = pd.read_csv(file_path)
except Exception as e:
    print(f"Error reading CSV: {e}")
    sys.exit(1)

# Check if 'File' column exists
if 'File' not in df.columns:
    print("Error: 'File' column not found in the dataset.")
    sys.exit(1)
    
# Clean column names
df.columns = df.columns.str.strip().str.replace('"', '').str.replace(' ', '')

# Identify runtime columns
time_cols = [col for col in df.columns if col.endswith('_time')]

# Method groups
dehb_group = [col for col in time_cols if re.match(r'DEHB-\d', col)]
act_group = [col for col in time_cols if re.match(r'LITE-\d', col)]
line_group = [col for col in time_cols if re.match(r'\s*\d', col) and not col.startswith("DEHB") and not col.startswith("LITE")]
random_group = [col for col in time_cols if re.match(r'\s*\d+r', col)]

# Output directory
output_dir = "../results/runtime_plot"
os.makedirs(output_dir, exist_ok=True)

# Store data for combined plot
combined_data = []

# Per-file plots
for file_name in df['File'].unique():
    subset = df[df['File'] == file_name]

    avg_dehb = subset[dehb_group].mean(axis=1).values[0] if dehb_group else None
    avg_act = subset[act_group].mean(axis=1).values[0] if act_group else None
    avg_line = subset[line_group].mean(axis=1).values[0] if line_group else None
    avg_random = subset[random_group].mean(axis=1).values[0] if random_group else None

    method_names = []
    performance = []
    entry = {"File": file_name}

    if avg_dehb is not None:
        method_names.append("DEHB")
        performance.append(avg_dehb)
        entry["DEHB"] = avg_dehb        
    if avg_act is not None:
        method_names.append("Active Learning")
        performance.append(avg_act)
        entry["LITE"] = avg_act
        
    if avg_line is not None:
        method_names.append("LINE")
        performance.append(avg_line)
        entry["LINE"] = avg_line

    if avg_random is not None:
        method_names.append("RANDOM")
        performance.append(avg_random)
        entry["RANDOM"] = avg_random


    combined_data.append(entry)
   
def clean_label(label):
    label = label.replace('.csv', '')
    label = label.replace('healthCloseIsses12mths0011-easy', 'Health-easy')
    label = label.replace('healthCloseIsses12mths0001-hard', 'Health-hard')
    return label

# Create DataFrame for combined plot
combined_df = pd.DataFrame(combined_data)

# Sort by LINE runtime
combined_df_sorted = combined_df.sort_values(by="LINE")
combined_df_sorted["File"] = combined_df_sorted["File"].apply(clean_label)
# Plotting all datasets (with log scale)
plt.figure(figsize=(9, 6))
x = combined_df_sorted["File"]
styles = {
    "DEHB": ('o', '-', 'tab:blue'),
    "LINE": ('s', '--', 'tab:green'),
    "RANDOM": ('^', '-.', 'tab:red'),
    "LITE": ('h', '-.', 'tab:pink'),
}

for method in ["DEHB", "LINE", "LITE", "RANDOM"]:
    if method in combined_df_sorted.columns:
        marker, linestyle, color = styles[method]
        plt.plot(x, combined_df_sorted[method], marker=marker,
        linestyle=linestyle,
        color=color, label=method)
plt.xticks(rotation=45, ha='right')
plt.yscale('log')  # Log scale
plt.ylabel("Avg. Runtime (log scale)",fontsize=12)
plt.xlabel("Dataset",fontsize=12)
plt.yticks(fontsize=11)
ax = plt.gca()
ax.tick_params(axis='y', labelsize=11)
# Update font size and legend position

#plt.title("Performance Comparison Across All Datasets")
legend = plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=len(styles), frameon=False, fontsize=14)
for text in legend.get_texts():
    text.set_fontsize(13)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "all_datasets_performance_comparison.png"))
plt.close()