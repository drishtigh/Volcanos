#!/usr/bin/env python
"""
Volcano Animation Creator.

This script generates an animated GIF of volcano locations, appearing
sequentially based on their 'Visual' score, with a blinking effect.

Usage (PowerShell):
  python create_animation.py
"""
from __future__ import annotations

import random
from pathlib import Path

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
except ImportError:
    print("pandas, matplotlib, and Pillow are required.")
    print("Install with: python -m pip install -r requirements.txt")
    raise

def create_volcano_animation():
    """
    Reads volcano data and creates a blinking, sequential animation of their appearance.
    """
    # --- 1. Data Loading and Preparation ---
    csv_path = Path(__file__).parent / 'data' / 'output.csv'
    if not csv_path.exists():
        print(f"Error: Data file not found at {csv_path}")
        return

    try:
        df = pd.read_csv(csv_path)
        df.rename(columns={'Latitude': 'Longitude', 'Longitude': 'Latitude'}, inplace=True)
        df['Max VEI'] = pd.to_numeric(df['Max VEI'], errors='coerce')
        df.dropna(subset=['Latitude', 'Longitude', 'Max VEI'], inplace=True)
        df['Max VEI'] = df['Max VEI'].astype(int)
        df['Visual'] = (df['Max VEI'] + 1) * 50
        
        # Sort by 'Visual' score to control appearance order
        df.sort_values('Visual', inplace=True)
        
        print("--- Data loaded and sorted for animation ---")
        print(f"Found {len(df)} volcanoes to animate.")

    except Exception as e:
        print(f"Error processing data: {e}")
        return

    # --- 2. Animation Setup ---
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_title('Volcano Eruption Sequence', color='white', fontsize=16)
    ax.set_xlabel('Longitude', color='gray')
    ax.set_ylabel('Latitude', color='gray')
    ax.grid(False)

    # Colormap and normalization
    cmap = plt.get_cmap('YlOrRd')
    norm = plt.Normalize(vmin=df['Max VEI'].min(), vmax=df['Max VEI'].max())
    
    # Prepare data for plotting
    x_coords = df['Longitude'].tolist()
    y_coords = df['Latitude'].tolist()
    sizes = df['Visual'].tolist()
    colors = cmap(norm(df['Max VEI'].tolist()))

    # --- 3. Animation Logic ---
    # This list will hold the scatter plot objects for visible points
    visible_scatter = []

    def update(frame):
        """
        The function called for each frame of the animation.
        - Adds one new volcano per frame.
        - Makes all currently visible volcanoes "blink".
        """
        ax.clear() # Clear previous frame's artists
        ax.set_facecolor('black')
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.set_title(f'Volcano Eruption Sequence (Volcano {frame+1}/{len(df)})', color='white', fontsize=16)
        ax.set_xlabel('Longitude', color='gray')
        ax.set_ylabel('Latitude', color='gray')
        ax.grid(False)

        # Get data for all volcanoes up to the current frame
        num_visible = frame + 1
        current_x = x_coords[:num_visible]
        current_y = y_coords[:num_visible]
        current_sizes = sizes[:num_visible]
        current_colors = colors[:num_visible]
        
        # To make them blink, generate new random alpha values for each circle each frame
        blinking_alphas = [random.uniform(0.3, 1.0) for _ in range(num_visible)]
        
        # Set the alpha for each individual circle color
        blinking_colors = [(*color[:3], alpha) for color, alpha in zip(current_colors, blinking_alphas)]

        ax.scatter(
            current_x,
            current_y,
            s=current_sizes,
            c=blinking_colors,
            marker='o'
        )
        return ax,

    # --- 4. Create and Save Animation ---
    print("--- Starting animation rendering (this may take a moment)... ---")
    # The number of frames is the number of volcanoes
    num_frames = len(df)
    
    anim = FuncAnimation(fig, update, frames=num_frames, blit=False, interval=100)

    output_path = Path(__file__).parent / 'volcano_animation.gif'
    
    # Use the 'pillow' writer for GIF creation
    anim.save(str(output_path), writer='pillow', fps=10)
    
    print(f"--- Animation Created ---")
    print(f"GIF saved to: {output_path}")

def main(argv: list[str] | None = None) -> int:
    create_volcano_animation()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
