#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  8 17:20:21 2025

@author: hetmodi
"""

import pandas as pd
import matplotlib.pyplot as plt

# --- Read Excel file ---
file_path = "/Users/hetmodi/Desktop/Research Module-2/Het/CCCV_Data/Anode_Potential_PID.xlsx"  # Update if file is in a different directory
df = pd.read_excel(file_path)

# --- Check column names (optional) ---
print(df.columns)

Time = df['Time']/1800

# --- Plot Time vs URN ---
plt.figure(figsize=(8, 5))
plt.plot(Time, df['urn'], color='blue', linewidth=1.5, label='PI-controlled (Anode Potential) – Cell-1')

# --- Add labels and formatting ---
plt.xlabel('Time /h', fontsize=14)
plt.ylabel('Anode Potential vs Li/Li+ /V', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=12, loc='best', frameon=False)
plt.tight_layout()

# --- Show or save plot ---

plt.savefig('PID_Anode_Potential.png', dpi=600, bbox_inches='tight') 
plt.show()