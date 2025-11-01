#!/usr/bin/env python
"""
Volcano Animation Creator with Connection Lines.

This script generates an animated GIF of volcano locations, appearing
sequentially based on their 'Visual' score, with a blinking effect
and lines connecting volcanoes of the same intensity.

Usage (PowerShell):
  python create_animation_with_lines.py
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

def create_volcano_animation_with_lines():
    """
    Reads volcano data and creates a staged animation: volcanoes appear
    by group, then lines are drawn to connect them.
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
        
        # Use index for tracking volcanoes
        df.reset_index(inplace=True)
        
        print("--- Data loaded for staged animation ---")

    except Exception as e:
        print(f"Error processing data: {e}")
        return

    # --- 2. Build Animation Event Sequence ---
    animation_events = []
    # Sort groups by Visual score to process them in order
    sorted_groups = df.groupby('Visual', sort=True)

    for visual_score, group in sorted_groups:
        # Sort volcanoes within the group by longitude for a predictable path
        group = group.sort_values('Longitude')
        
        # Event Phase 1: Volcanoes in the group appear one by one
        for volcano_index in group.index:
            animation_events.append({'type': 'appear', 'volcano_index': volcano_index})
            
        # Event Phase 2: Lines for this group are drawn one by one
        if len(group) > 1:
            coordinates = list(zip(group['Longitude'], group['Latitude']))
            vei_value = group['Max VEI'].iloc[0] # All have same VEI in a group
            
            for i in range(len(coordinates) - 1):
                segment = (coordinates[i], coordinates[i+1])
                animation_events.append({'type': 'draw_line', 'segment': segment, 'vei': vei_value})

    print(f"--- Created {len(animation_events)} animation events ---")

    # --- 3. Animation Setup ---
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 10))
    fig.patch.set_facecolor('black')
    
    cmap = plt.get_cmap('YlOrRd')
    norm = plt.Normalize(vmin=df['Max VEI'].min(), vmax=df['Max VEI'].max())

    visible_volcano_indices = set()
    visible_lines = []

    # --- 4. Animation Logic ---
    def update(frame):
        """
        The function called for each frame of the animation.
        Processes one event (volcano appearance or line drawing) per frame.
        """
        event = animation_events[frame]
        
        if event['type'] == 'appear':
            visible_volcano_indices.add(event['volcano_index'])
        elif event['type'] == 'draw_line':
            visible_lines.append(event)

        # --- Redraw the entire scene for this frame ---
        ax.clear()
        ax.set_facecolor('black')
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.set_title(f'Volcano Constellation Sequence (Event {frame+1}/{len(animation_events)})', color='white', fontsize=16)
        ax.set_xlabel('Longitude', color='gray')
        ax.set_ylabel('Latitude', color='gray')
        ax.grid(False)

        # Draw all lines that have appeared so far
        for line_event in visible_lines:
            start, end = line_event['segment']
            line_color = cmap(norm(line_event['vei']))
            ax.plot([start[0], end[0]], [start[1], end[1]], color=line_color, alpha=0.6, linewidth=0.9, zorder=5)

        # Draw all volcanoes that have appeared so far
        if visible_volcano_indices:
            visible_df = df.loc[list(visible_volcano_indices)]
            
            # Blinking effect
            blinking_alphas = [random.uniform(0.3, 1.0) for _ in range(len(visible_df))]
            visible_colors = cmap(norm(visible_df['Max VEI'].tolist()))
            blinking_colors = [(*color[:3], alpha) for color, alpha in zip(visible_colors, blinking_alphas)]

            ax.scatter(
                visible_df['Longitude'],
                visible_df['Latitude'],
                s=visible_df['Visual'],
                c=blinking_colors,
                marker='o',
                zorder=10
            )
        return ax,

    # --- 5. Create and Save Animation ---
    print("--- Starting staged animation rendering (this may take a while)... ---")
    num_frames = len(animation_events)
    
    anim = FuncAnimation(fig, update, frames=num_frames, blit=False, interval=150)

    output_path = Path(__file__).parent / 'volcano_animation_with_lines.gif'
    anim.save(str(output_path), writer='pillow', fps=15)
    
    print(f"--- Staged Animation with Lines Created ---")
    print(f"GIF saved to: {output_path}")

def main(argv: list[str] | None = None) -> int:
    create_volcano_animation_with_lines()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
