# Homolog Search Settings Configurations

This directory contains YAML configuration files for running homolog searches between different query protein sets and genome assemblies.

## Available Query Protein Sets

- **des**: Desaturases (`desaturases.fasta`)
- **hyl**: Hydroxylases (`hydroxylases.fasta`)
- **pks**: Polyketide synthases (`polyketide_synthases.fasta`)
- **pks_long**: Long polyketide synthases (`pks_long.fasta`)
- **elong**: Elongases (`elongases.fasta`)
- **decarb**: Decarboxylases (`decarboxylases.fasta`)

## Available Genomes

- **Chrsp_1**: Chrysochromulina tobin
- **IsochDm2_1**: Isochrysis galbana CCMP1323
- **Isogal1**: Isochrysis galbana
- **Gepoce1**: Gephyrocapsa oceanica
- **Ochro3194_1**: Ochrosphaera sp. CCMP3194
- **Pparv12B1_1_1**: Pavlova parvum
- **Phaglo1**: Phaeodactylum tricornutum
- **Chrpa1_1**: Chrysochromulina parva
- **Platy1217_1**: Prymnesium platychrysis sp

## Configuration File Naming Convention

Files are named using the pattern: `{query_type}_{genome_name}_settings.yaml`

Examples:
- `des_chrsp_1_settings.yaml` - Desaturases vs Chrysochromulina tobin
- `hyl_ochro3194_1_settings.yaml` - Hydroxylases vs Ochrosphaera sp. CCMP3194
- `pks_long_gepoce1_settings.yaml` - Long polyketide synthases vs Gephyrocapsa oceanica

## Total Configurations

- **6 query types** × **9 genomes** = **54 total configurations**

## Usage

To run a homolog search with a specific configuration:

```bash
python homolog_search.py --settings config/des_chrsp_1_settings.yaml
```

Or to validate settings without running:

```bash
python homolog_search.py --settings config/hyl_ochro3194_1_settings.yaml --validate
```

## Configuration Structure

Each settings file contains:

### Locations Section
- `input-dir`: Directory containing query protein files
- `output-dir`: Output directory for results
- `genome-fasta`: Path to genome assembly FASTA file
- `gff3-file`: Path to GFF3 annotation file
- `proteins-fasta`: Query protein FASTA file
- `blast-output`: BLAST output filename

### General Section
- `species`: Full species name
- `species-short`: Short species identifier
- `evalue`: E-value threshold for BLAST (default: 1e-5)
- `max-target-seqs`: Maximum target sequences per query (default: 10)
- `n-cores`: Number of CPU cores for BLAST (default: 4)

## File Locations

All genome and annotation files are located in their respective directories in the workspace root. Query protein files are located in the workspace root directory.

## Output Structure

Results will be organized in the output directory by species:
```
output/
├── Chrsp_1/
│   ├── Chrsp_1_proteins.fasta
│   ├── Chrsp_1_db.*
│   ├── Chrsp_1_blastp_desaturases.fasta.tsv
│   └── Chrsp_1_best_hits_desaturases.fasta.tsv
├── Ochro3194_1/
│   └── ...
└── ...
```

