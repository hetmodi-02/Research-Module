#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 16:25:59 2025

@author: hetmodi
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Load Excel files ---
file_path_cccv = '/Users/hetmodi/Desktop/Research Module-2/Het/Voltage_Relaxation_Data/CCCV_2.xlsx'
file_path_cell1 = '/Users/hetmodi/Desktop/Research Module-2/Het/Voltage_Relaxation_Data/Cell-2.xlsx'

df_cccv = pd.read_excel(file_path_cccv)
df_cell1 = pd.read_excel(file_path_cell1)

# --- Sort by Time (important for correct derivative) ---
df_cccv = df_cccv.sort_values('Time')
df_cell1 = df_cell1.sort_values('Time')

# --- Compute dV/dt (no smoothing) ---
df_cccv['dV/dt'] = np.gradient(df_cccv['Voltage'], df_cccv['Time'])
df_cell1['dV/dt'] = np.gradient(df_cell1['Voltage'], df_cell1['Time'])

# --- Remove extreme values (outliers) ---
threshold = 10  # adjust threshold depending on your data scale
df_cccv = df_cccv[np.abs(df_cccv['dV/dt']) < threshold]
df_cell1 = df_cell1[np.abs(df_cell1['dV/dt']) < threshold]

# --- Plot dV/dt vs Time ---
plt.figure(figsize=(8, 5))
plt.plot(df_cccv['Time'], df_cccv['dV/dt'], color='#d62728', linewidth=1.8, label='2C CCCV Charging')
plt.plot(df_cell1['Time'], df_cell1['dV/dt'], color='#1f77b4', linewidth=1.8, label='PID-controlled (Anode Potential) – Cell-1')

# --- Formatting ---
plt.title('Differential Voltage/Time vs Time (No Smoothing)', fontsize=16, fontweight='bold')
plt.xlabel('Time (h)', fontsize=14)
plt.ylabel('dV/dt (V/h)', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(fontsize=12, loc='best', frameon=False)

# --- Save high-quality plot ---
plt.tight_layout()
plt.savefig('Differential_Voltage_Time_vs_Time_NoSmoothing.png', dpi=600, bbox_inches='tight')
plt.show()