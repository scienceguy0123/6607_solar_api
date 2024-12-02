import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create figure folder
figure_direct = "./figure"
os.makedirs(figure_direct, exist_ok=True)

# Read the CSV file
df = pd.read_csv('deliverable2.csv')

# Filter out rows where OutputVerificationFlag = 1
df_filtered = df[df['OutputVerificationFlag'] == 0].copy()

# Prepare data for binning
df_filtered.loc[:, 'log_num_panels'] = np.log1p(df_filtered['NumPanels'])

# Create 8 bins using log-transformed number of panels (showing integers for bin edges)
df_filtered.loc[:, 'panel_bin'], bin_edges = pd.cut(
    df_filtered['log_num_panels'], bins=8, labels=False, retbins=True)
bin_edges = np.exp(bin_edges) - 1  # Convert log bin edges back to integers

# Prepare data for correlation analysis
columns_of_interest = ['NumPanels', 'YearlyEnergy', 'SolarArea']
df_subset = df_filtered[columns_of_interest]

# Pie Chart
plt.figure(figsize=(10, 8))
panel_bin_counts = df_filtered['panel_bin'].value_counts().sort_index()
plt.pie(panel_bin_counts,
        labels=[f'Bin {i+1}\n({int(bin_edges[i]):,}-{int(bin_edges[i+1]):,})' for i in range(len(panel_bin_counts))],
        autopct='%1.1f%%')
plt.title('Distribution of Solar Panel Counts (Log-transformed)')
plt.savefig(f'{figure_direct}/Pie_Chart.png')
plt.show()

# Boxplot for Solar Panel (NumPanels) only
plt.figure(figsize=(12, 8))
sns.boxplot(x=df_filtered['NumPanels'])
plt.title('Boxplot of Solar Panel Counts')
plt.xlabel('Number of Panels')
plt.savefig(f'{figure_direct}/Boxplot.png')
plt.show()

# Histogram with KDE, with x-axis showing integer ranges instead of log values
plt.figure(figsize=(10, 8))
sns.histplot(data=df_filtered, x='log_num_panels', kde=True)
plt.title('Histogram of Log-transformed Panel Counts')
plt.xlabel('Number of Panels (Original Range)')
plt.ylabel(f'{figure_direct}/Frequency')

# Adjust x-ticks to show corresponding integer ranges
log_ticks = np.arange(df_filtered['log_num_panels'].min(), df_filtered['log_num_panels'].max(), 1)
int_ticks = np.exp(log_ticks) - 1  # Convert log values back to integers
plt.xticks(log_ticks, [f'{int(val):,}' for val in int_ticks])
plt.savefig(f'{figure_direct}/Histogram_KDE.png')
plt.show()

# Pair_plot
sns.pairplot(df_subset, diag_kind='kde', plot_kws={'alpha': 0.7})
plt.suptitle('Scatter Plot Matrix of Solar Panel Metrics', y=1.02)
plt.savefig(f'{figure_direct}/Pair_Plot.png')
plt.show()

# Print additional information
print("Bin Edges (log-transformed):")
for i in range(len(bin_edges)-1):
    print(f"Bin {i+1}: {int(bin_edges[i]):,} - {int(bin_edges[i+1]):,}")

print("\nDescriptive Statistics:")
print(df_subset.describe())
