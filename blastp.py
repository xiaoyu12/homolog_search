from Bio import SeqIO
import os
import subprocess

# Create a BLAST database from a FASTA file
def create_blast_database(db_file, db_name):
    print("Creating BLAST database...")
    if os.path.exists(db_file+".phr"):
        print(f"BLAST database already exists: {db_name}")
        return
    subprocess.run([
        'makeblastdb',
        '-in', db_file,
        '-dbtype', 'prot',
        '-out', db_name
    ], check=True)

def run_command(cmd, check_error=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if check_error and result.returncode != 0:
            print(f"Command failed: {cmd}")
            print(f"Error: {result.stderr}")
        return result
    except Exception as e:
        print(f"Error running command: {e}")
        return None

# Run a BLASTP search
def run_blastp(query_file, db_name, blast_output_file, evalue = 1e-5, max_target_seqs = 10, n_cores = 1):
    print("Running BLASTP search...")
    blastp_cmd = [
        'blastp',
        '-query', query_file,
        '-db', db_name,
        '-out', blast_output_file,
        '-evalue', str(evalue),
        '-max_target_seqs', str(max_target_seqs),
        '-num_threads', str(n_cores),
        '-outfmt', '6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen slen qcovs',
    ]
    try:
        result = run_command(blastp_cmd)
    except Exception as e:
        print(f"Error running BLASTP: {e}")
        return None
    print(f"BLAST results saved to: {blast_output_file}")
    return result

# Parse BLAST results
def parse_blast_results(blast_output_file):
    print("Parsing BLAST results...")
    blast_results = []
    with open(blast_output_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            if not line.strip():
                continue
            fields = line.strip().split('\t')
            if len(fields) < 14:
                continue
            blast_results.append({
                'query_id': fields[0],
                'subject_id': fields[1],
                'pident': float(fields[2]),
                'length': int(fields[3]),
                'mismatch': int(fields[4]),
                'gapopen': int(fields[5]),
                'qstart': int(fields[6]),
                'qend': int(fields[7]),
                'sstart': int(fields[8]),
                'send': int(fields[9]),
                'evalue': float(fields[10]),
                'bitscore': float(fields[11]),
                'qlen': int(fields[12]),
                'slen': int(fields[13]),
                'qcovs': float(fields[14]) if len(fields) > 14 else 0
                }
            )
    print(f"Found {len(blast_results)} BLAST hits")
    # Show summary of results
    if blast_results:
        print("\nTop BLAST hits summary:")
        for i, hit in enumerate(blast_results[:10]):
            print(f"{i+1:2d}. Query: {hit['query_id']} -> Subject: {hit['subject_id']}")
            print(f"    Identity: {hit['pident']:.1f}%, E-value: {hit['evalue']:.2e}, Coverage: {hit['qcovs']:.1f}%")
    
    else:
        print("BLAST search failed")        
    return blast_results
        
# Analyze BLAST results
def analyze_blast_results(blast_results, query_proteins):
    print("Analyzing BLAST results...")
    results_by_query = {}
    for hit in blast_results:
        query_id = hit['query_id']
        if query_id not in results_by_query:
            results_by_query[query_id] = []
        results_by_query[query_id].append(hit)

    # Analyze results by query
    for query_id, hits in results_by_query.items():
        print(f"Query: {query_id}")
        query_seq = None
        for seq in query_proteins:  # query_proteins is now a list, no need for iter()
            if seq.id == query_id:
                query_seq = seq
                print(f"    Sequence: {seq.seq}")
                break
        if query_seq:
            print(f"Query length: {len(query_seq.seq)} amino acids")
            print(f"Query description: {query_seq.description}")
        print(f"Number of significant hits (E-value < 1e-5): {len(hits)}")

         # Analyze hits
        for i, hit in enumerate(hits):
            print(f"\n  Hit {i+1}:")
            print(f"    Subject ID: {hit['subject_id']}")
            print(f"    Identity: {hit['pident']:.1f}%")
            print(f"    E-value: {hit['evalue']:.2e}")
            print(f"    Bit score: {hit['bitscore']:.1f}")
            print(f"    Query coverage: {hit['qcovs']:.1f}%")
            print(f"    Alignment length: {hit['length']} aa")
            print(f"    Subject length: {hit['slen']} aa")
            
            # Determine significance
            if hit['pident'] >= 70 and hit['qcovs'] >= 80 and hit['evalue'] <= 1e-50:
                significance = "VERY HIGH (likely ortholog)"
            elif hit['pident'] >= 50 and hit['qcovs'] >= 70 and hit['evalue'] <= 1e-20:
                significance = "HIGH (likely ortholog)"
            elif hit['pident'] >= 30 and hit['qcovs'] >= 50 and hit['evalue'] <= 1e-5:
                significance = "MEDIUM (likely homolog)"
            else:
                significance = "LOW (possible homolog)"
            
            print(f"    Significance: {significance}")
        print("\n" + "="*60 + "\n")
    # Get the best hits for further analysis
    print("=== EXTRACTING SEQUENCES OF BEST HITS ===")
    best_hits = {}
    for query in query_proteins:  # query_proteins is now a list, no need for iter()
        query_id = query.id
        print(f"Processing query: {query_id}")
        if query_id in results_by_query:
            hits = results_by_query[query_id]
            best_hits[query_id] = hits[0]
            print(f"Best hit for {query_id}: {best_hits[query_id]['subject_id']}")
            print(f"    Identity: {best_hits[query_id]['pident']:.1f}%")
            print(f"    E-value: {best_hits[query_id]['evalue']:.2e}")
            print(f"    Bit score: {best_hits[query_id]['bitscore']:.1f}")
            print(f"    Query coverage: {best_hits[query_id]['qcovs']:.1f}%")
            print(f"    Alignment length: {best_hits[query_id]['length']} aa")
            print(f"    Subject length: {best_hits[query_id]['slen']} aa")
            best_hit = best_hits[query_id]
            if best_hit['pident'] >= 70 and best_hit['qcovs'] >= 80 and best_hit['evalue'] <= 1e-50:
                best_hits[query_id]['significance'] = "VERY HIGH (likely ortholog)"
            elif best_hit['pident'] >= 50 and best_hit['qcovs'] >= 60 and best_hit['evalue'] <= 1e-20:
                best_hits[query_id]['significance'] = "HIGH (likely ortholog)"
            elif best_hit['pident'] >= 30 and best_hit['qcovs'] >= 40 and best_hit['evalue'] <= 1e-5:
                best_hits[query_id]['significance'] = "MEDIUM (likely homolog)"
            else:
                best_hits[query_id]['significance'] = "LOW (possible homolog)"
            print(f"    Significance: {best_hits[query_id]['significance']}")
        else:
            # Set fields to None
            best_hits[query_id] = {
                'query_id': query.id,
                'subject_id': None,
                'pident': None,
                'evalue': None,
                'bitscore': None,
                'qcovs': None,
                'length': None,
                'mismatch': None,
                'gapopen': None,
                'qstart': None,
                'qend': None,
                'sstart': None,
                'send': None,
                'qlen': len(query.seq),
                'slen': None,
                'qcovs': 0,
                'significance': "NOT FOUND"
            }
            print(f"No hits found for {query_id}")
        print("\n" + "="*60 + "\n")
    return best_hits