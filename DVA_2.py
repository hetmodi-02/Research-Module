#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 19:21:25 2025

@author: hetmodi
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.signal import savgol_filter

# ---- USER INPUT -------------------------------------------------------------
DATASETS = [
    # (FILE, SHEET, LEGEND LABEL)
    (r"/Users/hetmodi/Desktop/Research Module-2/Het/PID_Controlled_Cell-1_Data/PAT_4123_DC2C_30_Pulse_Het.xlsx",
     "PAT_4123_DC2C_31_Pulse_HetCusto",
     "Cell 1"),

    (r"/Users/hetmodi/Desktop/Research Module-2/Het/PID_Controlled_Cell-2_Data/PAT_4116_DC2C_30_Pulse_Het.xlsx",
     "PAT_4116_DC2C_31_Pulse_HetCusto",
     "Cell 2"),

    (r"/Users/hetmodi/Desktop/Research Module-2/Het/CCCV_Data/CCCV_30.xlsx",
     "Sheet1",
     "Cell 3"),
]

HEADER_ROW   = 13
OUTPUT_XLSX  = "Combined_Line3_4_dVdQ_d2VdQ2_clean.xlsx"
OUTPUT_PNG_DV = "Combined_Line3_4_dVdQ_vs_capacity_clean.png"
OUTPUT_PNG_DV_ZOOM = "Combined_Line3_4_dVdQ_early5pct_zoom.png"
OUTPUT_PNG_D2 = "Combined_Line3_4_d2VdQ2_vs_capacity.png"
OUTPUT_PNG_D2_ZOOM = "Combined_Line3_4_d2VdQ2_early5pct_zoom.png"

SKIP_POINTS  = 1
DV_DQ_LIMIT  = 2.0
DV_DQ_MINABS = 0.0
LINES_TO_INCLUDE = [3]
EARLY_FRAC = 0.05

# Savitzky–Golay smoothing parameters
SG_WINDOW = 31   # must be odd; adjust for your data density (e.g. 21–51)
SG_ORDER  = 3    # polynomial order for smoothing
# ----------------------------------------------------------------------------


def load_line_data(file, sheet, label, skip_points):
    df = pd.read_excel(file, sheet_name=sheet, header=HEADER_ROW)
    df.columns = df.columns.str.strip()

    # check necessary columns
    for c in ["U[V]", "Ah[Ah]"]:
        if c not in df.columns:
            raise KeyError(f"Missing column {c} in {Path(file).name}")

    for c in ["Line", "U[V]", "Ah[Ah]"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # select requested lines if present
    if "Line" in df.columns:
        d = df[df["Line"].isin(LINES_TO_INCLUDE)]
    else:
        print(f"⚠️ No 'Line' column in {Path(file).name}, using all data.")
        d = df

    d = d.dropna(subset=["U[V]", "Ah[Ah]"]).reset_index(drop=True)

    if len(d) > skip_points:
        d = d.iloc[skip_points:].reset_index(drop=True)

    # relative capacity
    Q = d["Ah[Ah]"].to_numpy()
    Q_rel = Q - Q[0]
    if Q_rel[-1] < Q_rel[0]:
        Q_rel = -Q_rel
    V_raw = d["U[V]"].to_numpy()

    # Apply Savitzky–Golay smoothing to voltage
    if len(V_raw) >= SG_WINDOW:
        V_smooth = savgol_filter(V_raw, SG_WINDOW, SG_ORDER)
    else:
        V_smooth = V_raw.copy()

    # segment-wise diffs
    dQ = np.diff(Q_rel)
    dV = np.diff(V_smooth)
    Q_mid_Ah = 0.5 * (Q_rel[1:] + Q_rel[:-1])
    V_mid = 0.5 * (V_smooth[1:] + V_smooth[:-1])

    # 1st derivative (V/mAh)
    dVdQ_V_per_Ah = np.full_like(dQ, np.nan, dtype=float)
    nz = dQ != 0.0
    dVdQ_V_per_Ah[nz] = dV[nz] / dQ[nz]
    dVdQ_V_per_mAh = dVdQ_V_per_Ah / 1000.0

    # 2nd derivative (V/mAh²)
    cap_mAh = Q_mid_Ah * 1000.0
    if len(cap_mAh) >= 5:
        # apply slight smoothing to dV/dQ before differentiating
        dVdQ_smooth = savgol_filter(dVdQ_V_per_mAh, 11 if len(dVdQ_V_per_mAh) > 11 else 5, 2)
        d2VdQ2_V_per_mAh2 = np.gradient(dVdQ_smooth, cap_mAh)
    else:
        d2VdQ2_V_per_mAh2 = np.full_like(dVdQ_V_per_mAh, np.nan)

    out = pd.DataFrame({
        "capacity_mid_Ah": Q_mid_Ah,
        "capacity_mid_mAh": cap_mAh,
        "voltage_mid_V": V_mid,
        "voltage_smooth_V": np.interp(Q_mid_Ah, Q_rel, V_smooth),
        "dV_dQ_V_per_mAh": dVdQ_V_per_mAh,
        "d2V_dQ2_V_per_mAh2": d2VdQ2_V_per_mAh2,
        "Label": label,
        "Source_File": Path(file).stem
    })
    return out


def main():
    parts = []
    for f, s, lbl in DATASETS:
        try:
            parts.append(load_line_data(f, s, lbl, SKIP_POINTS))
        except Exception as e:
            print(f"❌ Error reading {Path(f).name}: {e}")

    combined = pd.concat(parts, ignore_index=True)

    # clean (same logic)
    band = combined["dV_dQ_V_per_mAh"].abs()
    clean = combined[(band <= DV_DQ_LIMIT) & (band >= DV_DQ_MINABS)].dropna().reset_index(drop=True)

    # save to Excel
    xlsx_path = Path(OUTPUT_XLSX)
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        clean.to_excel(writer, index=False, sheet_name="clean_data")
    print(f"✅ Saved Excel: {xlsx_path.resolve()}")

    # ---- Plot 1: dV/dQ full ----
    plt.figure()
    for lbl, g in clean.groupby("Label"):
        g = g.sort_values("capacity_mid_mAh")
        plt.plot(g["capacity_mid_mAh"], g["dV_dQ_V_per_mAh"], label=lbl)
    plt.xlabel("Capacity (mAh)")
    plt.ylabel("dV/dQ (V/mAh)")
    plt.legend(title="Dataset")
    plt.grid(True)
    plt.savefig(OUTPUT_PNG_DV, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved Plot: {OUTPUT_PNG_DV}")

    # ---- Plot 2: dV/dQ early 5% ----
    plt.figure()
    for lbl, g in clean.groupby("Label"):
        g = g.sort_values("capacity_mid_mAh")
        Qmax = g["capacity_mid_mAh"].max()
        m = g["capacity_mid_mAh"] <= EARLY_FRAC * Qmax
        if m.any():
            plt.plot(g.loc[m, "capacity_mid_mAh"], g.loc[m, "dV_dQ_V_per_mAh"], label=lbl)
    plt.xlabel("Capacity (mAh)")
    plt.ylabel("dV/dQ (V/mAh)")
    plt.title(f"Early region (first {int(EARLY_FRAC*100)}% of Q)")
    plt.legend(title="Dataset")
    plt.grid(True)
    plt.savefig(OUTPUT_PNG_DV_ZOOM, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved Plot: {OUTPUT_PNG_DV_ZOOM}")

    # ---- Plot 3: d2V/dQ2 full ----
    plt.figure()
    for lbl, g in clean.groupby("Label"):
        g = g.sort_values("capacity_mid_mAh")
        plt.plot(g["capacity_mid_mAh"], g["d2V_dQ2_V_per_mAh2"], label=lbl)
    plt.xlabel("Capacity (mAh)")
    plt.ylabel(r"$d^2V/dQ^2$ (V mAh$^{-2}$)")
    plt.legend(title="Dataset")
    plt.grid(True)
    plt.savefig(OUTPUT_PNG_D2, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved Plot: {OUTPUT_PNG_D2}")

    # ---- Plot 4: d2V/dQ2 early 5% ----
    plt.figure()
    for lbl, g in clean.groupby("Label"):
        g = g.sort_values("capacity_mid_mAh")
        Qmax = g["capacity_mid_mAh"].max()
        m = g["capacity_mid_mAh"] <= EARLY_FRAC * Qmax
        if m.any():
            plt.plot(g.loc[m, "capacity_mid_mAh"], g.loc[m, "d2V_dQ2_V_per_mAh2"], label=lbl)
    plt.xlabel("Capacity (mAh)")
    plt.ylabel(r"$d^2V/dQ^2$ (V mAh$^{-2}$)")
    plt.title(f"Early region (first {int(EARLY_FRAC*100)}% of Q)")
    plt.legend(title="Dataset")
    plt.grid(True)
    plt.savefig(OUTPUT_PNG_D2_ZOOM, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved Plot: {OUTPUT_PNG_D2_ZOOM}")

if __name__ == "__main__":
    main()
