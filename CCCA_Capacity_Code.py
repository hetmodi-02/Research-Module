#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 14:03:47 2025

@author: hetmodi
"""

import pandas as pd
import matplotlib.pyplot as plt

# Load both Excel files
file1 = '/Users/hetmodi/Desktop/Research Module-2/Het/Capacity/Cell-1.xlsx'        # Cell 1
file2 = '/Users/hetmodi/Desktop/Research Module-2/Het/Capacity/Cell-2.xlsx'  # Cell 2 (replace with your filename)

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# Plot
plt.figure(figsize=(7,5))

plt.plot(df1['Cycle'], df1['Capacity (mAh)'], marker='o', markersize=6,
         linestyle='-', linewidth=2, color='#4169E1', label='PI-controlled (Anode Potential) – Cell 1')
plt.plot(df2['Cycle'], df2['Capacity (mAh)'], marker='o', markersize=6,
         linestyle='-', linewidth=2, color='#FF7F0E', label='PI-controlled (Anode Potential) – Cell 2')

# Styling
plt.xlabel('Cycles', fontsize=14)
plt.ylabel('Capacity /mAh', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(fontsize=11, loc='best', frameon=False)

# Save high-quality figure
plt.tight_layout()
plt.savefig('Capacity_vs_Cycle_PID.png', dpi=600, bbox_inches='tight')
plt.show()