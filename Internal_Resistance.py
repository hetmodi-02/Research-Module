#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 12:01:48 2025

@author: hetmodi
"""

import pandas as pd
import matplotlib.pyplot as plt

# --- Load Excel files ---

file2 = '/Users/hetmodi/Desktop/Research Module-2/Het/Internal Resistance/Cell-1.xlsx'
file3 = '/Users/hetmodi/Desktop/Research Module-2/Het/Internal Resistance/Cell-2.xlsx'


df2 = pd.read_excel(file2)
df3 = pd.read_excel(file3)

# --- Ensure 'Cycles' is numeric ---

df2['Cycles'] = pd.to_numeric(df2['Cycles'], errors='coerce')
df3['Cycles'] = pd.to_numeric(df3['Cycles'], errors='coerce')

# --- Sort by Cycle (important) ---

df2 = df2.sort_values('Cycles')
df3 = df3.sort_values('Cycles')

# --- Plot ---
plt.figure(figsize=(8, 5))

plt.plot(df2['Cycles'], df2['Internal Resistance'], marker='o', markersize=6, linewidth=2,
         color='#008080', label='PI-controlled (Anode Potential) – Cell-1')
plt.plot(df3['Cycles'], df3['Internal Resistance'], marker='o', markersize=6, linewidth=2,
         color='#8000FF', label='PI-controlled (Anode Potential) – Cell-2')

# --- Formatting ---
plt.xlabel('Cycles', fontsize=14)
plt.ylabel('Internal Resistance /Ω', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(fontsize=12, loc='best', frameon=False)


# --- Save & show ---
plt.tight_layout()
plt.savefig('Internal_Resistance.png', dpi=600, bbox_inches='tight')
plt.show()