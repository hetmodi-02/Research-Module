#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 13:40:43 2025

@author: hetmodi
"""

import pandas as pd
import matplotlib.pyplot as plt

# --- Load Excel files ---
file1 = '/Users/hetmodi/Desktop/Research Module-2/Het/Internal Resistance/CCCV.xlsx'

df1 = pd.read_excel(file1)

# --- Ensure 'Cycles' is numeric ---
df1['Cycles'] = pd.to_numeric(df1['Cycles'], errors='coerce')

# --- Sort by Cycle (important) ---
df1 = df1.sort_values('Cycles')

# --- Plot ---
plt.figure(figsize=(8, 5))
plt.plot(df1['Cycles'], df1['Internal Resistance'], marker='o', markersize=6, linewidth=2,
         color='#FF6F61', label='2C CCCV Charging')

# --- Formatting ---
plt.xlabel('Cycles', fontsize=14)
plt.ylabel('Internal Resistance /Ω', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(fontsize=12, loc='best', frameon=False)


# --- Save & show ---
plt.tight_layout()
plt.savefig('Internal_Resistance_vs_Cycle_AllCells.png', dpi=600, bbox_inches='tight')
plt.show()