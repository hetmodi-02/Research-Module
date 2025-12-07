#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  8 16:17:52 2025

@author: hetmodi
"""

import pandas as pd
import matplotlib.pyplot as plt

# --- Read Excel file ---
file_path = "/Users/hetmodi/Desktop/Research Module-2/Het/CCCV_Data/Anode Potential.xlsx"
df = pd.read_excel(file_path)

# --- Check columns (optional) ---
print(df.columns)

# --- Add offset to Time column from row 62 till end ---
offset = 0.116430652314815
df.loc[60:, 'Time'] = df.loc[60:, 'Time'] + offset   # index 61 = line 62 (Python indexing starts from 0)

# --- Verify change ---
print(df.loc[60:65, 'Time'])

# --- Plot Time vs URN ---
plt.figure(figsize=(7,5))
plt.plot(df['Time'], df['urn'], color='#1f77b4', linewidth=2, label='2C CCCV Charging')

# --- Formatting ---
plt.xlabel('Time /h', fontsize=14)
plt.ylabel('Anode Potential vs Li/Li+ /V', fontsize=12)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(fontsize=12, loc='best', frameon=False)



plt.tight_layout()
plt.savefig('CCCV_Anode_Potential.png', dpi=600, bbox_inches='tight')
plt.show()