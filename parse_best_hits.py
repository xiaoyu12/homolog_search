#!/usr/bin/env python3
"""
Parse best hits results for a specific protein file across all genomes.
"""

import os
import pandas as pd
import glob
from pathlib import Path
import argparse
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

def parse_best_hits_file(file_path):
    """
    Parse a single best hits TSV file.
    
    Args:
        file_path (str): Path to the best hits file
        
    Returns:
        pd.DataFrame: Parsed data
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return pd.DataFrame()

def analyze_protein_results(protein_name, output_dir="output"):
    """
    Analyze best hits results for a specific protein across all genomes.
    
    Args:
        protein_name (str): Name of the protein file
        output_dir (str): Output directory path
        
    Returns:
        dict: Analysis results
    """
    print(f"Analyzing best hits for {protein_name} across all genomes...")
    print("=" * 80)
    
    # Find all best hits files
    best_hits_files = find_best_hits_files(protein_name, output_dir)
    
    if not best_hits_files:
        print(f"No best hits files found for {protein_name}")
        return {}
    
    print(f"Found best hits files for {len(best_hits_files)} genomes:")
    for genome, file_path in best_hits_files.items():
        print(f"  - {genome}: {os.path.basename(file_path)}")
    
    # Parse all files and combine results
    all_results = []
    genome_stats = {}
    
    for genome, file_path in best_hits_files.items():
        print(f"\nProcessing {genome}...")
        
        df = parse_best_hits_file(file_path)
        if df.empty:
            print(f"  No data found in {file_path}")
            continue
        
        # Add genome information
        df['genome'] = genome
        all_results.append(df)
        
        # Calculate statistics for this genome
        stats = {
            'total_queries': len(df),
            'queries_with_hits': len(df[df['subject_id'].notna()]),
            'queries_no_hits': len(df[df['subject_id'].isna()]),
            'high_significance': len(df[df['significance'].str.contains('HIGH', na=False)]),
            'medium_significance': len(df[df['significance'].str.contains('MEDIUM', na=False)]),
            'low_significance': len(df[df['significance'].str.contains('LOW', na=False)]),
            'very_low_significance': len(df[df['significance'].str.contains('VERY LOW', na=False)]),
            'not_found': len(df[df['significance'].str.contains('NOT FOUND', na=False)]),
            'avg_identity': df['pident'].mean() if 'pident' in df.columns else None,
            'avg_evalue': df['evalue'].mean() if 'evalue' in df.columns else None,
            'avg_bitscore': df['bitscore'].mean() if 'bitscore' in df.columns else None
        }
        
        genome_stats[genome] = stats
        
        print(f"  Queries: {stats['total_queries']}")
        print(f"  With hits: {stats['queries_with_hits']}")
        print(f"  High significance: {stats['high_significance']}")
        print(f"  Medium significance: {stats['medium_significance']}")
        print(f"  Low significance: {stats['low_significance']}")
        if stats['avg_identity']:
            print(f"  Avg identity: {stats['avg_identity']:.1f}%")
    
    # Combine all results
    if all_results:
        combined_df = pd.concat(all_results, ignore_index=True)
        
        # Overall statistics
        overall_stats = {
            'total_genomes': len(best_hits_files),
            'total_queries': len(combined_df),
            'total_hits': len(combined_df[combined_df['subject_id'].notna()]),
            'high_significance_total': len(combined_df[combined_df['significance'].str.contains('HIGH', na=False)]),
            'medium_significance_total': len(combined_df[combined_df['significance'].str.contains('MEDIUM', na=False)]),
            'low_significance_total': len(combined_df[combined_df['significance'].str.contains('LOW', na=False)]),
            'very_low_significance_total': len(combined_df[combined_df['significance'].str.contains('VERY LOW', na=False)]),
            'not_found_total': len(combined_df[combined_df['significance'].str.contains('NOT FOUND', na=False)])
        }
        
        return {
            'combined_data': combined_df,
            'genome_stats': genome_stats,
            'overall_stats': overall_stats,
            'best_hits_files': best_hits_files
        }
    
    return {}

def generate_summary_report(analysis_results, protein_name):
    """
    Generate a comprehensive summary report.
    
    Args:
        analysis_results (dict): Results from analyze_protein_results
        protein_name (str): Name of the protein file
    """
    if not analysis_results:
        print("No analysis results to report.")
        return
    
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE ANALYSIS REPORT FOR {protein_name.upper()}")
    print(f"{'='*80}")
    
    # Overall statistics
    overall = analysis_results['overall_stats']
    print(f"\nOVERALL STATISTICS:")
    print(f"  Total genomes analyzed: {overall['total_genomes']}")
    print(f"  Total queries: {overall['total_queries']}")
    print(f"  Total hits found: {overall['total_hits']}")
    print(f"  Hit rate: {overall['total_hits']/overall['total_queries']*100:.1f}%")
    
    print(f"\nSIGNIFICANCE BREAKDOWN:")
    print(f"  HIGH (likely orthologs): {overall['high_significance_total']}")
    print(f"  MEDIUM (likely homologs): {overall['medium_significance_total']}")
    print(f"  LOW (possible homologs): {overall['low_significance_total']}")
    print(f"  VERY LOW: {overall['very_low_significance_total']}")
    print(f"  NOT FOUND: {overall['not_found_total']}")
    
    # Per-genome breakdown
    print(f"\nPER-GENOME BREAKDOWN:")
    print(f"{'Genome':<20} {'Queries':<10} {'Hits':<8} {'High':<8} {'Med':<8} {'Low':<8}")
    print("-" * 70)
    
    for genome, stats in analysis_results['genome_stats'].items():
        print(f"{genome:<20} {stats['total_queries']:<10} {stats['queries_with_hits']:<8} "
              f"{stats['high_significance']:<8} {stats['medium_significance']:<8} {stats['low_significance']:<8}")
    
    # Top hits analysis
    print(f"\nTOP HITS ANALYSIS:")
    combined_df = analysis_results['combined_data']
    
    # Find highest identity hits
    high_identity = combined_df[combined_df['pident'].notna()].nlargest(5, 'pident')
    if not high_identity.empty:
        print(f"\nTop 5 hits by identity:")
        for _, row in high_identity.iterrows():
            print(f"  {row['query_id']} → {row['subject_id']} ({row['genome']}): "
                  f"{row['pident']:.1f}% identity, E-value: {row['evalue']:.2e}")
    
    # Find lowest E-value hits
    low_evalue = combined_df[combined_df['evalue'].notna()].nsmallest(5, 'evalue')
    if not low_evalue.empty:
        print(f"\nTop 5 hits by E-value:")
        for _, row in low_evalue.iterrows():
            print(f"  {row['query_id']} → {row['subject_id']} ({row['genome']}): "
                  f"E-value: {row['evalue']:.2e}, {row['pident']:.1f}% identity")

def save_analysis_results(analysis_results, protein_name, output_dir="analysis_output"):
    """
    Save analysis results to files.
    
    Args:
        analysis_results (dict): Results from analyze_protein_results
        protein_name (str): Name of the protein file
        output_dir (str): Directory to save results
    """
    if not analysis_results:
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save combined data
    combined_file = os.path.join(output_dir, f"{protein_name.replace('.fasta', '')}_all_genomes_combined.tsv")
    analysis_results['combined_data'].to_csv(combined_file, index=False, sep='\t')
    print(f"\nCombined data saved to: {combined_file}")
    
    # Save genome statistics
    stats_file = os.path.join(output_dir, f"{protein_name.replace('.fasta', '')}_genome_statistics.tsv")
    stats_df = pd.DataFrame(analysis_results['genome_stats']).T
    stats_df.to_csv(stats_file, sep='\t')
    print(f"Genome statistics saved to: {stats_file}")
    
    # Save summary report
    report_file = os.path.join(output_dir, f"{protein_name.replace('.fasta', '')}_analysis_report.txt")
    with open(report_file, 'w') as f:
        # Redirect print output to file
        import sys
        original_stdout = sys.stdout
        sys.stdout = f
        
        generate_summary_report(analysis_results, protein_name)
        
        sys.stdout = original_stdout
    
    print(f"Analysis report saved to: {report_file}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Parse best hits results for a specific protein across all genomes",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'protein_name',
        type=str,
        help='Name of the protein file (e.g., elongases.fasta)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory containing genome results (default: output)'
    )
    
    parser.add_argument(
        '--analysis-output',
        type=str,
        default='analysis_output',
        help='Directory to save analysis results (default: analysis_output)'
    )
    
    parser.add_argument(
        '--save-results',
        action='store_true',
        help='Save analysis results to files'
    )
    
    args = parser.parse_args()
    
    # Analyze results
    results = analyze_protein_results(args.protein_name, args.output_dir)
    
    if results:
        # Generate summary report
        generate_summary_report(results, args.protein_name)
        
        # Save results if requested
        if args.save_results:
            save_analysis_results(results, args.protein_name, args.analysis_output)
    else:
        print(f"No results found for {args.protein_name}")

if __name__ == "__main__":
    main()

