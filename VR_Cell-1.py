#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 15:39:29 2025

@author: hetmodi
"""

import pandas as pd
import matplotlib.pyplot as plt

# --- Load Excel files ---
file_path_cccv = '/Users/hetmodi/Desktop/Research Module-2/Het/Voltage_Relaxation_Data/CCCV_1.xlsx'
file_path_cell1 = '/Users/hetmodi/Desktop/Research Module-2/Het/Voltage_Relaxation_Data/Cell-1.xlsx'

df_cccv = pd.read_excel(file_path_cccv)
df_cell1 = pd.read_excel(file_path_cell1)

# --- Check column names (optional) ---
print(df_cccv.columns)
print(df_cell1.columns)

# --- Plot Time vs Voltage for both cells ---
plt.figure(figsize=(8, 5))
plt.plot(df_cccv['Time'], df_cccv['Voltage'], color='#d62728', linewidth=2, label='2C CCCV Charging')
plt.plot(df_cell1['Time'], df_cell1['Voltage'], color='#1f77b4', linewidth=2, label='PID-controlled (Anode Potential) – Cell-1')

# --- Add labels and formatting ---
plt.title('Time vs Voltage Comparison', fontsize=16, fontweight='bold')
plt.xlabel('Time (h)', fontsize=14)
plt.ylabel('Voltage (V)', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(fontsize=12, loc='best', frameon=False)

# --- Save high-quality image ---
plt.tight_layout()
plt.savefig('Time_vs_Voltage_Comparison.png', dpi=600, bbox_inches='tight')
plt.show()