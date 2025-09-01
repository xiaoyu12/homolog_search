#!/usr/bin/env python3
"""
Homolog Search Tool

This script demonstrates how to read a settings.yaml file as a command line option
and parse its contents for use in bioinformatics workflows.
"""

import argparse
import yaml
import os
import sys
import pandas as pd
from pathlib import Path
from Bio import SeqIO
from extract_proteins import parse_gff3_and_extract_proteins
from blastp import create_blast_database, run_blastp, parse_blast_results, analyze_blast_results

def load_settings(settings_file):
    """
    Load and parse settings from a YAML file.
    
    Args:
        settings_file (str): Path to the YAML settings file
        
    Returns:
        dict: Parsed settings from the YAML file
        
    Raises:
        FileNotFoundError: If the settings file doesn't exist
        yaml.YAMLError: If the YAML file is malformed
    """
    if not os.path.exists(settings_file):
        raise FileNotFoundError(f"Settings file not found: {settings_file}")
    
    try:
        with open(settings_file, 'r') as f:
            settings = yaml.safe_load(f)
        return settings
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file {settings_file}: {e}")


def validate_settings(settings):
    """
    Validate that required settings are present and files exist.
    
    Args:
        settings (dict): Parsed settings dictionary
        
    Returns:
        bool: True if settings are valid, False otherwise
    """
    required_sections = ['locations', 'general']
    
    # Check if required sections exist
    for section in required_sections:
        if section not in settings:
            print(f"Error: Missing required section '{section}' in settings file")
            return False
    
    # Check if required files exist
    locations = settings.get('locations', {})
    required_files = ['genome-fasta', 'gff3-file', 'proteins-fasta']
    
    for file_key in required_files:
        if file_key not in locations:
            print(f"Error: Missing required file path '{file_key}' in locations section")
            return False
        
        file_path = locations[file_key]
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
    
    return True


def print_settings_summary(settings):
    """
    Print a summary of the loaded settings.
    
    Args:
        settings (dict): Parsed settings dictionary
    """
    print("Settings Summary:")
    print("=" * 50)
    
    # Print locations
    if 'locations' in settings:
        print("\nLocations:")
        for key, value in settings['locations'].items():
            print(f"  {key}: {value}")
    
    # Print general settings
    if 'general' in settings:
        print("\nGeneral Settings:")
        for key, value in settings['general'].items():
            print(f"  {key}: {value}")

def homolog_search(settings):
    """
    Perform homolog search using the settings.
    """
    print("Performing homolog search...")
    print(f"Settings: {settings}")

    # Extract settings
    locations = settings['locations']
    general = settings['general']
    
    # Default settings
    if 'n-cores' not in general:
        general['n-cores'] = 1
        
    # Create output directory if it doesn't exist

    output_dir = locations.get('output-dir', 'proteins')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output directory this species
    output_dir = os.path.join(output_dir, general['species-short'])
    os.makedirs(output_dir, exist_ok=True)

    print(f"Running workflow with settings:")
    print(f"  Species: {general['species']}")
    print(f"  Genome: {locations['genome-fasta']}")

    # Extract proteins using settings
    genome_name = general['species'].replace(' ', '_')
    proteins = parse_gff3_and_extract_proteins(
        locations['gff3-file'],
        locations['genome-fasta'],
        genome_name
    )
    # Save proteins to file
    genome_short = general['species-short']
    output_file = os.path.join(output_dir, f"{genome_short}_proteins.fasta")
    if not os.path.exists(output_file):
        SeqIO.write(proteins, output_file, "fasta")
        print(f"Saved {len(proteins)} proteins to: {output_file}")

    # Create BLAST database
    create_blast_database(output_file, os.path.join(output_dir, f"{genome_short}_db"))

    # Run BLASTP search
    query_file = os.path.join(locations['input-dir'], locations['proteins-fasta'])
    # get the name of the query file
    query_name = os.path.basename(query_file)
    blast_output_file = os.path.join(output_dir, f"{genome_short}_blastp_{query_name}.tsv")
    run_blastp(query_file, os.path.join(output_dir, f"{genome_short}_db"), blast_output_file, 
        evalue=general['evalue'], max_target_seqs=general['max-target-seqs'], n_cores=general['n-cores'])

    # Parse BLAST results
    blast_results = parse_blast_results(blast_output_file)
    # Read the query file and convert to list so it can be reused multiple times
    query_file = os.path.join(locations['input-dir'], locations['proteins-fasta'])
    query_proteins = list(SeqIO.parse(query_file, "fasta"))  # Convert to list so it can be reused
    # Analyze BLAST results
    best_hits = analyze_blast_results(blast_results, query_proteins)
    
    # Write best hits to file
    summary_df = pd.DataFrame(best_hits)
    summary_df = summary_df.T
    summary_df.columns = ['query_id', 'subject_id', 'pident', 'length', 'mismatch', 'gapopen', 'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore', 'qlen', 'slen', 'qcovs', 'significance']
    summary_df.to_csv(os.path.join(output_dir, f"{genome_short}_best_hits_{query_name}.tsv"), index=False)
    

def main():
    """
    Main function to handle command line arguments and process settings.
    """
    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description="Homolog Search Tool - Read settings from YAML file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --settings settings.yaml
  %(prog)s -s config.yaml --validate
  %(prog)s --settings settings.yaml --summary
        """
    )
    
    parser.add_argument(
        '-s', '--settings',
        type=str,
        default='config/settings.yaml',
        help='Path to the YAML settings file (default: settings.yaml)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate settings and check if files exist'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print a summary of the loaded settings'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Parse command line arguments
    args = parser.parse_args()
    
    try:
        # Load settings from YAML file
        if args.verbose:
            print(f"Loading settings from: {args.settings}")
        
        settings = load_settings(args.settings)
        
        if args.verbose:
            print("Settings loaded successfully")
        
        # Validate settings if requested
        if args.validate:
            print("Validating settings...")
            if validate_settings(settings):
                print("✓ Settings validation passed")
            else:
                print("✗ Settings validation failed")
                sys.exit(1)
        
        # Print summary if requested
        if args.summary:
            print_settings_summary(settings)
        
        # Return settings for use in other parts of the application
        return settings
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    settings = main()
    
    # Example of how to use the settings
    if settings:
        print("\nExample usage of settings:")
        print(f"Genome file: {settings['locations']['genome-fasta']}")
        print(f"GFF3 file: {settings['locations']['gff3-file']}")
        print(f"E-value threshold: {settings['general']['evalue']}")
        print(f"Max target sequences: {settings['general']['max-target-seqs']}")

    homolog_search(settings)