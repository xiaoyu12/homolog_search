#!/usr/bin/env python3
"""
Generate bubble plots and heatmaps for protein best hits analysis.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import glob
from collections import defaultdict

def find_best_hits_files(protein_name, output_dir="output"):
    """
    Find all best hits files for a specific protein across all genomes.
    
    Args:
        protein_name (str): Name of the protein file (e.g., 'elongases.fasta')
        output_dir (str): Output directory path
        
    Returns:
        dict: Dictionary mapping genome names to best hits file paths
    """
    best_hits_files = {}
    
    # Get all genome directories
    genome_dirs = [d for d in os.listdir(output_dir) 
                   if os.path.isdir(os.path.join(output_dir, d))]
    
    for genome in genome_dirs:
        # Look for best hits file for this protein
        pattern = f"{genome}_best_hits_{protein_name}"
        files = glob.glob(os.path.join(output_dir, genome, f"{pattern}.tsv"))
        
        if files:
            best_hits_files[genome] = files[0]
    
    return best_hits_files

def load_best_hits_data(protein_name, output_dir="output"):
    """
    Load and combine best hits data for a protein across all genomes.
    
    Args:
        protein_name (str): Name of the protein file
        output_dir (str): Output directory path
        
    Returns:
        pd.DataFrame: Combined data with genome information
    """
    best_hits_files = find_best_hits_files(protein_name, output_dir)
    
    if not best_hits_files:
        print(f"No best hits files found for {protein_name}")
        return pd.DataFrame()
    
    all_data = []
    
    for genome, file_path in best_hits_files.items():
        try:
            df = pd.read_csv(file_path)
            df['genome'] = genome
            all_data.append(df)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()

def create_bubble_plot(data, protein_name, output_dir="visualizations"):
    """
    Create a bubble plot showing significance and quality of matches.
    
    Args:
        data (pd.DataFrame): Combined best hits data
        protein_name (str): Name of the protein file
        output_dir (str): Output directory for plots
    """
    if data.empty:
        print(f"No data available for {protein_name}")
        return
    
    # Set up the plot
    plt.figure(figsize=(14, 8))
    
    # Get unique queries and genomes
    queries = sorted(data['query_id'].unique())
    genomes = sorted(data['genome'].unique())
    
    # Create significance mapping
    significance_map = {
        'VERY HIGH (likely ortholog)': {'color': 'red', 'size': 200, 'alpha': 0.8},
        'HIGH (likely ortholog)': {'color': 'orange', 'size': 150, 'alpha': 0.8},
        'MEDIUM (likely homolog)': {'color': 'yellow', 'size': 100, 'alpha': 0.8},
        'LOW (possible homolog)': {'color': 'green', 'size': 50, 'alpha': 0.8},
        'NOT FOUND': {'color': 'gray', 'size': 10, 'alpha': 0.4}
    }
    
    # Create the plot
    for i, query in enumerate(queries):
        for j, genome in enumerate(genomes):
            # Get data for this query-genome combination
            subset = data[(data['query_id'] == query) & (data['genome'] == genome)]
            
            if subset.empty:
                # No data - plot as NOT FOUND
                plt.scatter(j, i, s=10, c='gray', alpha=0.4, edgecolors='black', linewidth=0.5)
                plt.text(j, i, 'NF', ha='center', va='center', fontsize=8, fontweight='bold')
            else:
                # Get the best hit (highest identity)
                # Handle case where pident might be NaN
                valid_subset = subset.dropna(subset=['pident'])
                if not valid_subset.empty:
                    best_hit = valid_subset.loc[valid_subset['pident'].idxmax()]
                    significance = best_hit['significance']
                    identity = best_hit['pident']
                else:
                    # All pident values are NaN
                    significance = 'NOT FOUND'
                    identity = 0
                
                # Get plot parameters
                if significance in significance_map:
                    params = significance_map[significance]
                else:
                    params = significance_map['NOT FOUND']
                
                # Plot the bubble
                plt.scatter(j, i, s=params['size'], c=params['color'], 
                           alpha=params['alpha'], edgecolors='black', linewidth=0.5)
                
                # Add identity text
                plt.text(j, i, f'{identity:.1f}%', ha='center', va='center', 
                        fontsize=8, fontweight='bold')
    
    # Customize the plot
    plt.xticks(range(len(genomes)), genomes, rotation=45, ha='right')
    plt.yticks(range(len(queries)), queries)
    plt.xlabel('Genomes')
    plt.ylabel('Query Proteins')
    plt.title(f'{protein_name.replace(".fasta", "").replace("_", " ").title()} - Best Hits Analysis')
    
    # Add legend
    legend_elements = []
    for sig, params in significance_map.items():
        legend_elements.append(plt.scatter([], [], s=params['size'], c=params['color'], 
                                         alpha=params['alpha'], label=sig))
    
    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adjust layout and save
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the plot
    output_file = os.path.join(output_dir, f"{protein_name.replace('.fasta', '')}_bubble_plot.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Bubble plot saved to: {output_file}")

def create_heatmap(data, protein_name, output_dir="visualizations"):
    """
    Create a heatmap showing percent identity values.
    
    Args:
        data (pd.DataFrame): Combined best hits data
        protein_name (str): Name of the protein file
        output_dir (str): Output directory for plots
    """
    if data.empty:
        print(f"No data available for {protein_name}")
        return
    
    # Get unique queries and genomes
    queries = sorted(data['query_id'].unique())
    genomes = sorted(data['genome'].unique())
    
    # Create identity matrix
    identity_matrix = np.zeros((len(queries), len(genomes)))
    
    for i, query in enumerate(queries):
        for j, genome in enumerate(genomes):
            # Get data for this query-genome combination
            subset = data[(data['query_id'] == query) & (data['genome'] == genome)]
            
            if not subset.empty:
                # Get the best hit (highest identity)
                # Handle case where pident might be NaN
                valid_subset = subset.dropna(subset=['pident'])
                if not valid_subset.empty:
                    best_hit = valid_subset.loc[valid_subset['pident'].idxmax()]
                    identity_matrix[i, j] = best_hit['pident']
                else:
                    identity_matrix[i, j] = 0
            else:
                identity_matrix[i, j] = 0
    
    # Create the heatmap
    plt.figure(figsize=(12, 8))
    
    # Use RdYlBu_r colormap (red-yellow-blue reversed)
    sns.heatmap(identity_matrix, 
                xticklabels=genomes, 
                yticklabels=queries,
                cmap='RdYlBu_r',
                annot=True,
                fmt='.1f',
                cbar_kws={'label': 'Percent Identity (%)'},
                vmin=0,
                vmax=100)
    
    plt.title(f'{protein_name.replace(".fasta", "").replace("_", " ").title()} - Percent Identity Heatmap')
    plt.xlabel('Genomes')
    plt.ylabel('Query Proteins')
    
    # Adjust layout and save
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the plot
    output_file = os.path.join(output_dir, f"{protein_name.replace('.fasta', '')}_heatmap.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Heatmap saved to: {output_file}")

def generate_visualizations_for_protein(protein_name, output_dir="output", viz_dir="visualizations"):
    """
    Generate both bubble plot and heatmap for a specific protein.
    
    Args:
        protein_name (str): Name of the protein file
        output_dir (str): Directory containing analysis results
        viz_dir (str): Directory to save visualizations
    """
    print(f"Generating visualizations for {protein_name}...")
    
    # Load data
    data = load_best_hits_data(protein_name, output_dir)
    
    if data.empty:
        print(f"No data found for {protein_name}")
        return
    
    print(f"Found data for {len(data['query_id'].unique())} queries across {len(data['genome'].unique())} genomes")
    
    # Generate plots
    create_bubble_plot(data, protein_name, viz_dir)
    create_heatmap(data, protein_name, viz_dir)

def generate_all_visualizations(output_dir="output", viz_dir="visualizations"):
    """
    Generate visualizations for all protein families.
    
    Args:
        output_dir (str): Directory containing analysis results
        viz_dir (str): Directory to save visualizations
    """
    # Define protein families
    protein_families = [
        'elongases.fasta',
        'desaturases.fasta', 
        'hydroxylases.fasta',
        'polyketide_synthases.fasta',
        'pks_long.fasta',
        'decarboxylases.fasta'
    ]
    
    print("Generating visualizations for all protein families...")
    print("=" * 60)
    
    for protein in protein_families:
        generate_visualizations_for_protein(protein, output_dir, viz_dir)
        print()
    
    print("All visualizations generated!")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate bubble plots and heatmaps for protein best hits analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--protein',
        type=str,
        help='Specific protein file to visualize (e.g., elongases.fasta)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Directory containing analysis results (default: output)'
    )
    
    parser.add_argument(
        '--viz-dir',
        type=str,
        default='visualizations',
        help='Directory to save visualizations (default: visualizations)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate visualizations for all protein families'
    )
    
    args = parser.parse_args()
    
    if args.all:
        generate_all_visualizations(args.output_dir, args.viz_dir)
    elif args.protein:
        generate_visualizations_for_protein(args.protein, args.output_dir, args.viz_dir)
    else:
        print("Please specify either --protein or --all")
        parser.print_help()

if __name__ == "__main__":
    main()
