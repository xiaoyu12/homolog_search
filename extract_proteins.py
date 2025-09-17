print("Step 1: Extracting protein sequences from genomes")
print("=" * 50)

import re
from Bio.SeqUtils import gc_fraction
from collections import defaultdict
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

output_dir = "proteins"

def parse_gff3_and_extract_proteins(gff_path, genome_path, genome_name):
    """Extract protein sequences from genome using GFF3 annotations"""
    
    # Load genome sequences
    print(f"Loading {genome_name} genome sequences...")
    genome_seqs = {}
    for record in SeqIO.parse(genome_path, "fasta"):
        genome_seqs[record.id] = record.seq
    print(f"Loaded {len(genome_seqs)} scaffolds")
    
    # Parse GFF3 to extract CDS features
    print(f"Parsing {genome_name} GFF3 annotations...")
    cds_features = defaultdict(list)
    gene_info = {}
    
    with open(gff_path, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
                
            parts = line.strip().split('\t')
            if len(parts) < 9:
                continue
                
            scaffold, source, feature_type, start, end, score, strand, phase, attributes = parts
            
            if feature_type == 'CDS':
                # Parse attributes
                attr_dict = {}
                for attr in attributes.split(';'):
                    if '=' in attr:
                        key, value = attr.split('=', 1)
                        attr_dict[key] = value
                
                # Extract protein ID
                protein_id = None
                if 'Parent' in attr_dict:
                    parent_id = attr_dict['Parent']
                    if parent_id.startswith('mRNA_'):
                        protein_id = parent_id
                
                if protein_id:
                    cds_features[protein_id].append({
                        'scaffold': scaffold,
                        'start': int(start),
                        'end': int(end),
                        'strand': strand,
                        'phase': int(phase) if phase.isdigit() else 0
                    })
                if 'product' in attr_dict:
                    gene_info[protein_id]['product'] = attr_dict['product']

            elif feature_type == 'mRNA':
                # Store gene information
                attr_dict = {}
                for attr in attributes.split(';'):
                    if '=' in attr:
                        key, value = attr.split('=', 1)
                        attr_dict[key] = value
                
                if 'ID' in attr_dict:
                    gene_info[attr_dict['ID']] = {
                        'name': attr_dict.get('Name', ''),
                        'proteinId': attr_dict.get('proteinId', ''),
                        'product': attr_dict.get('product', '')
                    }
    
    print(f"Found {len(cds_features)} genes with CDS features")
    
    # Extract and translate CDS sequences
    proteins = []
    for protein_id, cds_list in cds_features.items():
        if not cds_list:
            continue
            
        # Sort CDS by start position
        cds_list.sort(key=lambda x: x['start'])
        
        # Get scaffold sequence
        scaffold_id = cds_list[0]['scaffold']
        if scaffold_id not in genome_seqs:
            continue
            
        scaffold_seq = genome_seqs[scaffold_id]
        
        # Extract and concatenate CDS sequences
        cds_seq = ""
        for cds in cds_list:
            start = cds['start'] - 1  # Convert to 0-based
            end = cds['end']
            cds_part = scaffold_seq[start:end]
            cds_seq += str(cds_part)
        
        # Reverse complement if on negative strand
        if cds_list[0]['strand'] == '-':
            cds_seq = str(Seq(cds_seq).reverse_complement())
        
        # Translate to protein
        try:
            protein_seq = str(Seq(cds_seq).translate())
            # Remove stop codon if present at the end
            if protein_seq.endswith('*'):
                protein_seq = protein_seq[:-1]
            
            # Create protein record
            gene_name = gene_info.get(protein_id, {}).get('name', protein_id)
            protein_id_clean = gene_info.get(protein_id, {}).get('proteinId', protein_id)
            product = gene_info.get(protein_id, {}).get('product', '')
            
            description = f"{protein_id_clean} {gene_name}"
            if product:
                description += f" | {product}"
            
            protein_record = SeqRecord(
                Seq(protein_seq),
                id=protein_id_clean,
                description=description
            )
            proteins.append(protein_record)
            
        except Exception as e:
            # Skip problematic sequences
            continue
    
    print(f"Successfully extracted {len(proteins)} protein sequences")
    return proteins

