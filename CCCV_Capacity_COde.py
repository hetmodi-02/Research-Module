#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 13:08:50 2025

@author: hetmodi
"""

import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file
file_path = '/Users/hetmodi/Desktop/Research Module-2/Het/Capacity/CCCV_Capacity.xlsx'
df = pd.read_excel(file_path)

# Plot
plt.figure(figsize=(7,5))
plt.plot(df['Cycle'], df['Capacity'], marker='o', markersize=6, 
         linestyle='-', linewidth=2, color='Red', label='2C CCCV Charging')

# Styling
plt.xlabel('Cycles', fontsize=14)
plt.ylabel('Capacity /mAh', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(fontsize=12, loc='best', frameon=False)


plt.savefig('Capacity_vs_Cycle(CCCV).png', dpi=600, bbox_inches='tight') 
plt.show()