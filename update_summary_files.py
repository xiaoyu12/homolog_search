#!/usr/bin/env python3
"""
Update genome performance and protein families summary files.
"""

import pandas as pd
import glob
import os

def update_summary_files():
    """Update the summary files with current data."""
    
    # Read all genome statistics files
    stats_files = glob.glob('analysis_output/*_genome_statistics.tsv')
    all_stats = []

    for file in stats_files:
        protein = os.path.basename(file).replace('_genome_statistics.tsv', '')
        df = pd.read_csv(file, sep='\t', index_col=0)
        df['protein_family'] = protein
        all_stats.append(df)

    # Combine all statistics
    combined_stats = pd.concat(all_stats)

    # Create genome performance summary
    genome_performance = []
    genomes = sorted(combined_stats.index.unique())
    
    for genome in genomes:
        subset = combined_stats.loc[genome]
        total_queries = subset['total_queries'].sum()
        total_hits = subset['queries_with_hits'].sum()
        high_orthologs = subset['high_significance'].sum()
        medium_homologs = subset['medium_significance'].sum()
        low_possible = subset['low_significance'].sum()
        very_low = subset['very_low_significance'].sum()
        not_found = subset['not_found'].sum()
        avg_identity = subset['avg_identity'].mean()
        proteins_analyzed = len(subset)
        hit_rate = (total_hits / total_queries * 100) if total_queries > 0 else 0
        
        genome_performance.append({
            'Total_Queries': total_queries,
            'Total_Hits': total_hits,
            'HIGH_Orthologs': high_orthologs,
            'MEDIUM_Homologs': medium_homologs,
            'LOW_Possible': low_possible,
            'VERY_LOW': very_low,
            'NOT_FOUND': not_found,
            'Avg_Identity_%': avg_identity,
            'Proteins_Analyzed': proteins_analyzed,
            'Hit_Rate_%': hit_rate
        })
    
    genome_perf_df = pd.DataFrame(genome_performance, index=genomes)
    genome_perf_df.to_csv('analysis_output/genome_performance_summary.tsv', sep='\t')
    
    # Create protein families summary
    protein_families = []
    for protein in sorted(combined_stats['protein_family'].unique()):
        subset = combined_stats[combined_stats['protein_family'] == protein]
        total_queries = subset['total_queries'].sum()
        total_hits = subset['queries_with_hits'].sum()
        hit_rate = (total_hits / total_queries * 100) if total_queries > 0 else 0
        high_orthologs = subset['high_significance'].sum()
        medium_homologs = subset['medium_significance'].sum()
        low_possible = subset['low_significance'].sum()
        very_low = subset['very_low_significance'].sum()
        not_found = subset['not_found'].sum()
        avg_identity = subset['avg_identity'].mean()
        
        protein_families.append({
            'Protein_Family': protein,
            'Total_Queries': total_queries,
            'Total_Hits': total_hits,
            'Hit_Rate_%': hit_rate,
            'HIGH_Orthologs': high_orthologs,
            'MEDIUM_Homologs': medium_homologs,
            'LOW_Possible': low_possible,
            'VERY_LOW': very_low,
            'NOT_FOUND': not_found,
            'Avg_Identity_%': avg_identity
        })
    
    protein_fam_df = pd.DataFrame(protein_families)
    protein_fam_df.to_csv('analysis_output/protein_families_summary.tsv', sep='\t', index=False)
    
    print("Summary files updated!")
    print(f"Genome performance summary: {len(genomes)} genomes")
    print(f"Protein families summary: {len(protein_families)} families")

if __name__ == "__main__":
    update_summary_files()
