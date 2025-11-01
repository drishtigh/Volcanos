#!/usr/bin/env python
"""
Volcano World Map Generator.

This script reads volcano data from a CSV file and generates an interactive
world map, which is saved as an HTML file.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

try:
    import folium
except ImportError:
    print("Folium is not installed. Please install it by running: pip install folium")
    exit()

def get_color(vei):
    """Returns a color based on the Volcanic Explosivity Index (VEI)."""
    if vei <= 1:
        return 'yellow'
    elif vei <= 3:
        return 'orange'
    else:
        return 'red'

def create_world_map():
    """
    Generates an interactive world map of volcanoes.
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
        
        # Clean 'Max VEI' data
        df['Max VEI'] = pd.to_numeric(df['Max VEI'], errors='coerce')
        df.dropna(subset=['Latitude', 'Longitude', 'Max VEI'], inplace=True)
        df['Max VEI'] = df['Max VEI'].astype(int)

    except Exception as e:
        print(f"Error processing data: {e}")
        return

    # Create a Folium map centered on an average location
    map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
    world_map = folium.Map(location=map_center, zoom_start=2, tiles='CartoDB dark_matter')

    # Add volcanoes to the map
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=(row['Max VEI'] + 1) * 2,  # Radius based on VEI
            color=get_color(row['Max VEI']),
            fill=True,
            fill_color=get_color(row['Max VEI']),
            fill_opacity=0.7,
            popup=f"<strong>{row['Volcano']}</strong><br>Max VEI: {row['Max VEI']}"
        ).add_to(world_map)

    # Save the map to an HTML file
    output_path = Path(__file__).parent / 'volcano_world_map.html'
    world_map.save(str(output_path))
    
    print(f"--- Interactive World Map Created ---")
    print(f"Map saved to: {output_path}")

if __name__ == "__main__":
    create_world_map()
