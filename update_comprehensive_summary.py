#!/usr/bin/env python3
"""
Update comprehensive summary with all protein families and genomes including Platy1217_1.
"""

import pandas as pd
import glob
import os

def update_comprehensive_summary():
    """Update the comprehensive summary file."""
    
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

    # Create comprehensive summary
    summary_lines = []
    summary_lines.append('')
    summary_lines.append('COMPREHENSIVE ANALYSIS SUMMARY')
    summary_lines.append('==============================')
    summary_lines.append('')
    summary_lines.append(f'Analysis completed for {len(combined_stats["protein_family"].unique())} protein families across {len(combined_stats.index.unique())} genomes.')
    summary_lines.append('')
    
    # Protein family overview
    summary_lines.append('PROTEIN FAMILY OVERVIEW:')
    summary_lines.append('     Protein_Family  Total_Queries  Total_Hits  Hit_Rate_%  HIGH_Orthologs  MEDIUM_Homologs  LOW_Possible  VERY_LOW  NOT_FOUND  Avg_Identity_%')

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
        
        summary_lines.append(f'       {protein:<15} {total_queries:>12.0f} {total_hits:>10.0f} {hit_rate:>9.1f} {high_orthologs:>13.0f} {medium_homologs:>14.0f} {low_possible:>11.0f} {very_low:>8.0f} {not_found:>9.0f} {avg_identity:>14.1f}')

    summary_lines.append('')
    summary_lines.append('GENOME PERFORMANCE OVERVIEW:')
    summary_lines.append('               Total_Queries  Total_Hits  HIGH_Orthologs  MEDIUM_Homologs  LOW_Possible  VERY_LOW  NOT_FOUND  Avg_Identity_%  Proteins_Analyzed  Hit_Rate_%')

    # Genome performance
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
        
        summary_lines.append(f'{genome:<20} {total_queries:>12.0f} {total_hits:>10.0f} {high_orthologs:>13.0f} {medium_homologs:>14.0f} {low_possible:>11.0f} {very_low:>8.0f} {not_found:>9.0f} {avg_identity:>14.1f} {proteins_analyzed:>16.0f} {hit_rate:>9.1f}')

    summary_lines.append('')
    summary_lines.append('Files saved in: analysis_output/')
    
    # Save to file
    with open('analysis_output/comprehensive_summary.txt', 'w') as f:
        f.write('\n'.join(summary_lines))
    
    print("Comprehensive summary updated!")
    print(f"Total protein families: {len(combined_stats['protein_family'].unique())}")
    print(f"Total genomes: {len(genomes)}")
    print(f"Genomes: {', '.join(genomes)}")

if __name__ == "__main__":
    update_comprehensive_summary()
