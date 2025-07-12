#!/usr/bin/env python3
"""
GATSol standardized batch wrapper for benchmarking
- Accepts: --fasta <input.fasta> --out <output.csv>
- Requires: matching PDB files for each sequence in the FASTA
- Runs the full GATSol pipeline and outputs a unified benchmarking CSV
"""
import os
import sys
import argparse
import tempfile
import shutil
import subprocess
import pandas as pd
from Bio import SeqIO

WRAPPER_PREDICTOR_NAME = "GATSol"


def parse_fasta(fasta_path):
    seqs = []
    for record in SeqIO.parse(fasta_path, "fasta"):
        seqs.append((record.id, str(record.seq)))
    return seqs


def write_list_csv(seqs, path):
    df = pd.DataFrame(seqs, columns=["id", "sequence"])
    df.to_csv(path, index=False)


def write_fasta_dir(seqs, outdir):
    os.makedirs(outdir, exist_ok=True)
    for sid, seq in seqs:
        with open(os.path.join(outdir, f"{sid}.fasta"), "w") as f:
            f.write(f">{sid}\n{seq}\n")


def check_pdbs(seqs, pdb_dir):
    missing = []
    for sid, _ in seqs:
        pdb_path = os.path.join(pdb_dir, f"{sid}.pdb")
        if not os.path.isfile(pdb_path):
            missing.append(sid)
    return missing


def run_pipeline(predict_dir):
    # Predict.sh expects to be run from within the tools dir
    subprocess.run(["bash", "Predict.sh"], cwd=os.path.join(predict_dir, "tools"), check=True)


def standardize_output(csv_path, fasta_seqs, out_path):
    df = pd.read_csv(csv_path)
    # df must have id, sequence, Solubility_hat
    out_rows = []
    for _, row in df.iterrows():
        acc = row["id"]
        seq = row["sequence"]
        score = row["Solubility_hat"]
        # GATSol outputs a single score, so set probabilities as NA
        out_rows.append({
            "Accession": acc,
            "Sequence": seq,
            "Predictor": WRAPPER_PREDICTOR_NAME,
            "SolubilityScore": score,
            "Probability_Soluble": "NA",
            "Probability_Insoluble": "NA"
        })
    pd.DataFrame(out_rows).to_csv(out_path, index=False)


def main():
    parser = argparse.ArgumentParser(description="GATSol batch wrapper for benchmarking.")
    parser.add_argument("--fasta", required=True, help="Input FASTA file")
    parser.add_argument("--out", required=True, help="Output CSV file")
    parser.add_argument("--predict_dir", default="Predict", help="Path to GATSol Predict dir")
    args = parser.parse_args()

    fasta_path = os.path.abspath(args.fasta)
    out_csv = os.path.abspath(args.out)
    predict_dir = os.path.abspath(args.predict_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Prepare input dirs
        need_dir = os.path.join(predict_dir, "NEED_to_PREPARE")
        fasta_dir = os.path.join(need_dir, "fasta")
        pdb_dir = os.path.join(need_dir, "pdb")
        os.makedirs(fasta_dir, exist_ok=True)
        os.makedirs(pdb_dir, exist_ok=True)
        # Parse FASTA
        seqs = parse_fasta(fasta_path)
        # Check PDBs
        missing = check_pdbs(seqs, pdb_dir)
        if missing:
            print(f"Error: Missing PDBs for: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
        # Write fasta files and list.csv
        write_fasta_dir(seqs, fasta_dir)
        write_list_csv(seqs, os.path.join(need_dir, "list.csv"))
        # Run pipeline
        run_pipeline(predict_dir)
        # Standardize output
        standardize_output(os.path.join(predict_dir, "Output.csv"), seqs, out_csv)
        print(f"Done. Results written to {out_csv}")

if __name__ == "__main__":
    main()
