#!/usr/bin/env python3
"""
Data Analysis and Visualization for Strain Gauge Measurements
Reads CSV log files and generates plots
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

def analyze_csv(csv_file):
    """Load and analyze CSV data"""
    
    if not Path(csv_file).exists():
        print(f"Error: File not found: {csv_file}")
        sys.exit(1)
    
    # Load data
    df = pd.read_csv(csv_file)
    
    print("\n" + "="*50)
    print(f"Data File: {csv_file}")
    print("="*50)
    
    # Basic statistics
    print(f"\nTotal samples: {len(df)}")
    print(f"Duration: {df['Timestamp_ms'].iloc[-1] - df['Timestamp_ms'].iloc[0]} ms")
    print(f"  ({(df['Timestamp_ms'].iloc[-1] - df['Timestamp_ms'].iloc[0])/1000:.1f} seconds)")
    
    print(f"\nWeight Statistics:")
    print(f"  Min: {df['Weight_g'].min():.3f} g")
    print(f"  Max: {df['Weight_g'].max():.3f} g")
    print(f"  Mean: {df['Weight_g'].mean():.3f} g")
    print(f"  Std Dev: {df['Weight_g'].std():.3f} g")
    
    print(f"\nRaw Value Statistics:")
    print(f"  Min: {df['RawValue'].min()}")
    print(f"  Max: {df['RawValue'].max()}")
    print(f"  Mean: {df['RawValue'].mean():.0f}")
    
    # Create visualizations
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot 1: Weight over time
    axes[0].plot(df['Timestamp_ms'], df['Weight_g'], 'b-', linewidth=1)
    axes[0].set_xlabel('Time (ms)')
    axes[0].set_ylabel('Weight (g)')
    axes[0].set_title('Strain Gauge Measurement Over Time')
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Raw values
    axes[1].plot(df['Timestamp_ms'], df['RawValue'], 'r-', linewidth=0.5, alpha=0.7)
    axes[1].set_xlabel('Time (ms)')
    axes[1].set_ylabel('Raw ADC Value')
    axes[1].set_title('HX711 Raw Values')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_file = Path(csv_file).stem + '_plot.png'
    plt.savefig(output_file, dpi=150)
    print(f"\n✓ Plot saved: {output_file}")
    
    # Show plot
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_data.py <csv_file>")
        print("\nExample:")
        print("  python analyze_data.py ../data/strain_gauge_20260304_143025.csv")
        sys.exit(1)
    
    analyze_csv(sys.argv[1])
