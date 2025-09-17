#!/usr/bin/env python3
"""
Example script showing how to integrate YAML settings with the main workflow.
"""

import argparse
import yaml
import os
import sys
from extract_proteins import parse_gff3_and_extract_proteins
from Bio import SeqIO
import subprocess


def load_settings(settings_file):
    """Load and parse settings from a YAML file."""
    if not os.path.exists(settings_file):
        raise FileNotFoundError(f"Settings file not found: {settings_file}")
    
    with open(settings_file, 'r') as f:
        return yaml.safe_load(f)


def run_workflow_with_settings(settings):
    """
    Run the main workflow using settings from YAML file.
    
    Args:
        settings (dict): Parsed settings from YAML file
    """
    # Extract settings
    locations = settings['locations']
    general = settings['general']
    
    # Create output directory if it doesn't exist
    output_dir = locations.get('output-dir', 'proteins')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Running workflow with settings:")
    print(f"  Species: {general['species']}")
    print(f"  Genome: {locations['genome-fasta']}")
    print(f"  GFF3: {locations['gff3-file']}")
    print(f"  Output directory: {output_dir}")
    print(f"  E-value: {general['evalue']}")
    print(f"  Max target sequences: {general['max-target-seqs']}")
    print("=" * 50)
    
    # Extract proteins using settings
    genome_name = general['species'].replace(' ', '_')
    proteins = parse_gff3_and_extract_proteins(
        locations['gff3-file'],
        locations['genome-fasta'],
        genome_name
    )
    
    # Save proteins to file
    output_file = os.path.join(output_dir, f"{genome_name}_proteins.fasta")
    SeqIO.write(proteins, output_file, "fasta")
    print(f"Saved {len(proteins)} proteins to: {output_file}")
    
    # Run BLAST if available
    try:
        result = subprocess.run(['blastp', '-version'], capture_output=True, text=True)
        print("BLAST is available, running similarity search...")
        
        # Create BLAST database
        db_name = os.path.join(output_dir, f"{genome_name}_db")
        subprocess.run([
            'makeblastdb',
            '-in', output_file,
            '-dbtype', 'prot',
            '-out', db_name
        ], check=True)
        
        # Run BLAST search
        blast_output = os.path.join(output_dir, locations['blast-output'])
        subprocess.run([
            'blastp',
            '-query', locations['proteins-fasta'],
            '-db', db_name,
            '-out', blast_output,
            '-outfmt', '6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore stitle',
            '-evalue', str(general['evalue']),
            '-max_target_seqs', str(general['max-target-seqs'])
        ], check=True)
        
        print(f"BLAST results saved to: {blast_output}")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("BLAST not available or failed to run")
    except Exception as e:
        print(f"Error running BLAST: {e}")


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Run homolog search workflow with YAML settings",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-s', '--settings',
        type=str,
        default='settings.yaml',
        help='Path to the YAML settings file (default: settings.yaml)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate settings without running workflow'
    )
    
    args = parser.parse_args()
    
    try:
        # Load settings
        print(f"Loading settings from: {args.settings}")
        settings = load_settings(args.settings)
        
        # Validate settings
        required_sections = ['locations', 'general']
        for section in required_sections:
            if section not in settings:
                print(f"Error: Missing required section '{section}' in settings file")
                sys.exit(1)
        
        locations = settings['locations']
        required_files = ['genome-fasta', 'gff3-file', 'proteins-fasta']
        for file_key in required_files:
            if file_key not in locations:
                print(f"Error: Missing required file path '{file_key}' in locations section")
                sys.exit(1)
        
        print("✓ Settings validation passed")
        
        if args.validate_only:
            print("Validation only mode - exiting")
            return
        
        # Run workflow
        run_workflow_with_settings(settings)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

