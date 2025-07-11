# Truncate lacZ.pdb to the first 1010 residues in chain A, outputting lacZ_trunc.pdb
# Usage: python truncate_pdb_to_seq.py

input_pdb = 'lacZ.pdb'
output_pdb = 'lacZ_trunc.pdb'
max_residues = 1010  # exact length from lacZ.fasta
chain_id = 'A'

with open(input_pdb) as inp, open(output_pdb, 'w') as out:
    for line in inp:
        if line.startswith("ATOM") or line.startswith("HETATM"):
            res_chain = line[21]
            try:
                res_num = int(line[22:26])
            except ValueError:
                out.write(line)
                continue
            if res_chain == chain_id and res_num > max_residues:
                continue
        out.write(line)

print(f"Truncated {input_pdb} to first {max_residues} residues in chain {chain_id} -> {output_pdb}")
