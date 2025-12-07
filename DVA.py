import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ---- USER INPUT -------------------------------------------------------------
DATASETS = [
    # (FILE, SHEET, LEGEND LABEL)
    (r"/Users/hetmodi/Desktop/Research Module-2/Het/PID_Controlled_Cell-1_Data/PAT_4123_DC2C_1_Het.xlsx",
     "PAT_4123_DC1C_1_HetCustomCell_G",
     "Cell 1"),

    (r"/Users/hetmodi/Desktop/Research Module-2/Het/PID_Controlled_Cell-2_Data/PAT_4116_DC2C_1_Pulse_Het.xlsx",
     "PAT_4116_DC2C_1_Pulse_HetCusto",
     "Cell 2"),

    (r"/Users/hetmodi/Desktop/Research Module-2/Het/CCCV_Data/CCCV_30.xlsx",
     "Sheet1",
     "Cell 3"),
]

HEADER_ROW   = 13
OUTPUT_XLSX  = "Combined_Line3_4_dVdQ_vs_capacity_clean.xlsx"
OUTPUT_PNG_DV = "Combined_Line3_4_dVdQ_vs_capacity_clean.png"
OUTPUT_PNG_DV_ZOOM = "Combined_Line3_4_dVdQ_early5pct_zoom.png"
OUTPUT_PNG_D2 = "Combined_Line3_4_d2VdQ2_vs_capacity.png"
OUTPUT_PNG_D2_ZOOM = "Combined_Line3_4_d2VdQ2_early5pct_zoom.png"

SKIP_POINTS  = 1
DV_DQ_LIMIT  = 2      # max allowed |dV/dQ| (V/mAh)
DV_DQ_MINABS = -1  # drop near-zeros if wanted (>0), else keep your default
LINES_TO_INCLUDE = [3]     # e.g., [3] or [3,4]
EARLY_FRAC = 0.05
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

    # relative capacity (monotonic, positive)
    Q = d["Ah[Ah]"].to_numpy()
    Q_rel = Q - Q[0]
    if Q_rel[-1] < Q_rel[0]:
        Q_rel = -Q_rel
    V = d["U[V]"].to_numpy()

    # segment midpoints
    dQ = np.diff(Q_rel)
    dV = np.diff(V)
    Q_mid_Ah = 0.5 * (Q_rel[1:] + Q_rel[:-1])
    V_mid = 0.5 * (V[1:] + V[:-1])

    # 1st derivative: dV/dQ in V/Ah -> convert to V/mAh for plotting
    dVdQ_V_per_Ah = np.full_like(dQ, np.nan, dtype=float)
    nz = dQ != 0.0
    dVdQ_V_per_Ah[nz] = dV[nz] / dQ[nz]
    dVdQ_V_per_mAh = dVdQ_V_per_Ah / 1000.0

    # 2nd derivative: d2V/dQ2 in V/mAh^2
    # compute from mid-series using non-uniform grid aware gradient
    # use capacity in mAh for clarity and consistent units
    cap_mAh = Q_mid_Ah * 1000.0
    # gradient of (dV/dQ in V/mAh) w.r.t. capacity (mAh) -> V/mAh^2
    # safe if at least 3 points
    if len(cap_mAh) >= 3:
        d2VdQ2_V_per_mAh2 = np.gradient(dVdQ_V_per_mAh, cap_mAh)
    else:
        d2VdQ2_V_per_mAh2 = np.full_like(dVdQ_V_per_mAh, np.nan)

    out = pd.DataFrame({
        "capacity_mid_Ah": Q_mid_Ah,
        "capacity_mid_mAh": cap_mAh,
        "voltage_mid_V": V_mid,
        "dV_V": dV,
        "dQ_Ah": dQ,
        "dV_dQ_V_per_mAh": dVdQ_V_per_mAh,
        "d2V_dQ2_V_per_mAh2": d2VdQ2_V_per_mAh2,
        "Label": label,
        "Source_File": Path(file).stem
    })
    return out

def main():
    # Load and stack
    parts = []
    for f, s, lbl in DATASETS:
        try:
            parts.append(load_line_data(f, s, lbl, SKIP_POINTS))
        except Exception as e:
            print(f"❌ Error reading {Path(f).name}: {e}")

    combined = pd.concat(parts, ignore_index=True)

    # Clean the same way as before (band-pass on |dV/dQ|)
    clean = combined[
        ~((combined["dV_V"] == 0) |
          (combined["dQ_Ah"] == 0) |
          (combined["dV_dQ_V_per_mAh"] == 0))
    ].dropna().reset_index(drop=True)

    band = clean["dV_dQ_V_per_mAh"].abs()
    clean = clean[(band <= DV_DQ_LIMIT) & (band >= DV_DQ_MINABS)].reset_index(drop=True)

    # ---- Save to Excel (2 sheets) ----
    xlsx_path = Path(OUTPUT_XLSX)
    # Use openpyxl to avoid needing xlsxwriter
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        clean.to_excel(writer, index=False, sheet_name="clean_data")
    print(f"✅ Saved Excel: {xlsx_path.resolve()}")

    # ---- Plot: dV/dQ full ----
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
    print(f"✅ Saved Plot: {Path(OUTPUT_PNG_DV).resolve()}")

    # ---- Plot: dV/dQ early 5% ----
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
    print(f"✅ Saved Plot: {Path(OUTPUT_PNG_DV_ZOOM).resolve()}")

    # ---- Plot: d2V/dQ2 full ----
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
    print(f"✅ Saved Plot: {Path(OUTPUT_PNG_D2).resolve()}")

    # ---- Plot: d2V/dQ2 early 5% ----
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
    print(f"✅ Saved Plot: {Path(OUTPUT_PNG_D2_ZOOM).resolve()}")

if __name__ == "__main__":
    main()

