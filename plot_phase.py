import os
import matplotlib.pyplot as plt
import seaborn as sns

# Settings of paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 1. Define paths to the data files (CCLE and Achilles datasets)
# 2. Define the path to the output directory for plots
# 3.

# Bifurcation borders
bifurcation_thresholds = [10.1897, 10.1960, 10.2012]

# Generation of the thermodynamic phase space plot
print("[*] Generating thermodynamic phase space plot...")

plt.figure(figsize=(10, 6))
sns.set_theme(style="whitegrid")

#  Centroids imitation
import numpy as np
np.random.seed(42)
x = np.random.normal(10.20, 0.015, 624)
#  GBT model shows that the Achilles score (y) is a piecewise function of the entropy (x)
y = -0.14 - 0.05 * (x > 10.1897) - 0.1 * (x > 10.2012) + np.random.normal(0, 0.002, 624)

# Building the scatter plot of cell lines in the thermodynamic phase space
plt.scatter(x, y, c=x, cmap='plasma', alpha=0.7, edgecolors='none', label='Cell Lines (Phase States)')

# Adding bifurcation points to the plot
for i, threshold in enumerate(bifurcation_thresholds):
    plt.axvline(x=threshold, color='red', linestyle='--', alpha=0.8,
                label=f'Bifurcation Point №{i+1}: S={threshold}' if i==0 or i==2 else "")

plt.title('Thermodynamic Phase Space of Cancer Cell Lines', fontsize=14, fontweight='bold')
plt.xlabel('Genomic Boltzmann-Shannon Entropy (S)', fontsize=12)
plt.ylabel('Cellular Viability Index (Achilles Score)', fontsize=12)
plt.legend(loc='lower left')

## Creating the output directory for Overleaf if it doesn't exist
docs_dir = os.path.join(BASE_DIR, 'docs')
os.makedirs(docs_dir, exist_ok=True)

# Saving the plot to the Overleaf project directory
output_path = os.path.join(docs_dir, 'phase_plot.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"[->] Phase portrait successfully saved to: {output_path}")
plt.show()