import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

NODES_FILE = "nodes.txt"
VOLTAGES_FILE = "voltages.txt"

def load_nodes(filename):
    print("Loading nodes...")
    with open(filename, "r") as f:
        lines = f.readlines()

    cleaned_lines = []
    for line in lines:
        parts = line.strip().split()
        if 2 <= len(parts) <= 4:  # skip lines with >4 columns
            cleaned_lines.append(line)

    df = pd.read_csv(
        io.StringIO("".join(cleaned_lines)),
        sep=r"\s+",
        header=None,
        names=["Node", "X", "Y", "Layer"],
        dtype={"Node": str}
    )
    df["Node"] = df["Node"].str.upper()
    df["X"] = pd.to_numeric(df["X"], errors="coerce").astype("Int64")
    df["Y"] = pd.to_numeric(df["Y"], errors="coerce").astype("Int64")
    print(df.head())
    return df

def load_voltages(filename):
    print("Loading voltages...")
    with open(filename, "r") as f:
        lines = f.readlines()

    cleaned_lines = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            cleaned_lines.append(" ".join(parts[:2]) + "\n")

    df = pd.read_csv(
        io.StringIO("".join(cleaned_lines)),
        sep=r"\s+",
        header=None,
        names=["Node", "Voltage"],
        dtype={"Node": str}
    )
    df["Node"] = df["Node"].str.upper()
    df["Voltage"] = pd.to_numeric(df["Voltage"], errors="coerce")
    print(df.head())
    return df

def merge_data(nodes_df, voltages_df):
    print("Merging data...")
    merged = pd.merge(nodes_df, voltages_df, on="Node", how="inner")
    print(merged.head())
    return merged

def plot_heatmap(merged_df):
    print("Plotting heatmap...")

    # Pivot into a grid of voltages (Y as rows, X as columns)
    pivot_table = merged_df.pivot_table(
        index="Y", columns="X", values="Voltage", aggfunc="mean"
    )

    x_coords = pivot_table.columns.values
    y_coords = pivot_table.index.values

    plt.figure(figsize=(8, 6))
    plt.imshow(
        pivot_table.values,
        cmap="jet",  # jet = red-hot style common in EDA
        extent=[x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()],
        origin="lower",
        aspect="equal",        # keep aspect ratio like a real chip layout
        interpolation="bicubic"  # smoother than bilinear
    )

    # Add colorbar and labels
    cbar = plt.colorbar()
    cbar.set_label("Voltage (V)")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("IR Drop Heatmap")

    # Optional: flip Y axis if your layout’s origin is top-left
    # plt.gca().invert_yaxis()

    plt.show()

def main():
    nodes = load_nodes(NODES_FILE)
    voltages = load_voltages(VOLTAGES_FILE)
    merged = merge_data(nodes, voltages)
    plot_heatmap(merged)

if __name__ == "__main__":
    main()
