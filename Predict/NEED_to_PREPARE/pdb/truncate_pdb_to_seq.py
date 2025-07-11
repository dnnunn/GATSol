# Truncate a PDB file to match the number of residues in a given sequence (from FASTA or list.csv)
# Usage: python truncate_pdb_to_seq.py lacZ.pdb lacZ_trunc.pdb <sequence_length> <chain_id>
# Example: python truncate_pdb_to_seq.py lacZ.pdb lacZ_trunc.pdb 1010 A

import sys

if len(sys.argv) != 5:
    print("Usage: python truncate_pdb_to_seq.py <input_pdb> <output_pdb> <sequence_length> <chain_id>")
    sys.exit(1)

input_pdb = sys.argv[1]
output_pdb = sys.argv[2]
max_residues = int(sys.argv[3])
chain_id = sys.argv[4]

written_residues = set()

with open(input_pdb) as inp, open(output_pdb, 'w') as out:
    for line in inp:
        if line.startswith("ATOM") or line.startswith("HETATM"):
            # Extract chain and residue number
            res_chain = line[21]
            res_num = int(line[22:26])
            if res_chain == chain_id and res_num > max_residues:
                continue
        out.write(line)

print(f"Truncated {input_pdb} to first {max_residues} residues in chain {chain_id} -> {output_pdb}")
