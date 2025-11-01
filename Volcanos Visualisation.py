#!/usr/bin/env python
"""Volcano Visualization Helper.

Creates a "starry sky" plot of volcano locations using data from a CSV file.

Usage (PowerShell):
  python "Volcanos Visualisation.py"
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    import pandas as pd
    import matplotlib.pyplot as plt
except Exception as e:  # pragma: no cover - user missing deps
    print("pandas and matplotlib are required. Install with: python -m pip install -r requirements.txt")
    raise


from itertools import combinations

def visualize_volcano_sky():
    """
    Reads volcano data, filters for valid 'Max VEI' integers, and visualizes
    their locations as stars in a black sky with color and size based on intensity.
    """
    # Path to the CSV file
    csv_path = Path(__file__).parent / 'data' / 'output.csv'

    if not csv_path.exists():
        print(f"Error: Data file not found at {csv_path}")
        return

    # Read and clean data
    try:
        df = pd.read_csv(csv_path)
        
        # Swap Latitude and Longitude columns
        df.rename(columns={'Latitude': 'Longitude', 'Longitude': 'Latitude'}, inplace=True)
        
        # Convert 'Max VEI' to numeric, coercing errors (like '–') to NaN
        df['Max VEI'] = pd.to_numeric(df['Max VEI'], errors='coerce')
        
        # Drop rows where 'Max VEI' could not be converted or is missing
        df.dropna(subset=['Latitude', 'Longitude', 'Max VEI'], inplace=True)
        
        # Convert 'Max VEI' to integer
        df['Max VEI'] = df['Max VEI'].astype(int)

        # Create 'Visual' column for star size, and make stars 5 times bigger
        df['Visual'] = (df['Max VEI'] + 1) * 50

        # Display a few rows of the updated dataframe
        print("--- Updated Dataframe Preview ---")
        print(df[['Volcano', 'Max VEI', 'Visual', 'Longitude', 'Latitude']].head())
        print("-" * 30)

    except Exception as e:
        print(f"Error processing data: {e}")
        return

    # --- Create the "Starry Sky" Visualization ---
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')

    # --- Set up colormap to match star colors ---
    cmap = plt.get_cmap('plasma')
    norm = plt.Normalize(vmin=df['Max VEI'].min(), vmax=df['Max VEI'].max())

    # --- Connect stars with the same Visual score in a chain ---
    for visual_score, group in df.groupby('Visual'):
        # All stars in a group have the same VEI, so we can get the color from the first one
        vei_value = group['Max VEI'].iloc[0]
        line_color = cmap(norm(vei_value))

        coordinates = list(zip(group['Longitude'], group['Latitude']))
        if len(coordinates) > 1:
            # Sort by longitude to create a more predictable path
            coordinates.sort()
            for i in range(len(coordinates) - 1):
                start = coordinates[i]
                end = coordinates[i+1]
                ax.plot([start[0], end[0]], [start[1], end[1]], color=line_color, alpha=0.6, linewidth=0.9, zorder=5)

    # Plot volcanoes as stars with size and color based on Max VEI
    scatter = ax.scatter(
        df['Longitude'], 
        df['Latitude'], 
        s=df['Visual'],           # Size based on the new 'Visual' column
        c=df['Max VEI'],          # Color based on VEI
        cmap=cmap,                # Use the same colormap
        norm=norm,                # And the same normalization
        marker='*',
        alpha=0.9,
        edgecolor='white',
        linewidth=0.5,
        zorder=10                 # Ensure stars are plotted on top of the lines
    )

    # Customize the plot
    ax.set_title('Volcano Chains with Matched Colors', color='white', fontsize=16)
    ax.set_xlabel('Longitude', color='gray')
    ax.set_ylabel('Latitude', color='gray')
    ax.grid(False)
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)

    # Add a colorbar to serve as a legend for VEI
    cbar = fig.colorbar(scatter, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label('Max Volcanic Explosivity Index (VEI)', color='white')
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

    # Save the figure
    output_path = Path(__file__).parent / 'volcano_chains_colored.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='black')
    
    print(f"--- 'Volcano Chains' Map Updated ---")
    print(f"Image saved to: {output_path}")


def main(argv: list[str] | None = None) -> int:
    visualize_volcano_sky()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
