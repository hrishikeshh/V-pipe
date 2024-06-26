# GROUP: global
# CONDA: haploclique = 1.3.1
# CONDA: pysam = 0.19.0
# CONDA: biopython = 1.79

import subprocess
from pathlib import Path

import pysam
from Bio import SeqIO


def main(fname_bam, fname_reference, fname_result, dname_work):
    dname_work.mkdir(parents=True, exist_ok=True)

    # fix CIGAR by converting = and X to M
    fname_bam_fixed = fname_bam.parent / "reads.fixed.bam"

    with pysam.AlignmentFile(fname_bam, "rb") as bam_in:
        with pysam.AlignmentFile(
            fname_bam_fixed, "wb", header=bam_in.header
        ) as bam_out:
            for read in bam_in.fetch(until_eof=True):
                if read.cigarstring is not None:
                    read.cigarstring = read.cigarstring.replace("X", "M").replace(
                        "=", "M"
                    )
                bam_out.write(read)

    # run tool
    subprocess.run(
        [
            "haploclique",
            "--no_singletons",
            "--no_prob0",
            "--edge_quasi_cutoff_cliques=0.85",
            "--edge_quasi_cutoff_mixed=0.85",
            "--edge_quasi_cutoff_single=0.8",
            "--min_overlap_cliques=0.6",
            "--min_overlap_single=0.5",
            "--limit_clique_size=3",
            "--max_cliques=10000",
            fname_bam_fixed.resolve(),
        ],
        cwd=dname_work,
        check=True,
    )

    (dname_work / "quasispecies.fasta").rename(fname_result)

    # fix frequency information
    record_list = []
    for record in SeqIO.parse(fname_result, "fasta"):
        props = dict(
            pair.split(":") for pair in record.description.split("|") if ":" in pair
        )
        record.description = f"freq:{props['ht_freq']}"

        record_list.append(record)
    SeqIO.write(record_list, fname_result, "fasta")


if __name__ == "__main__":
    main(
        Path(snakemake.input.fname_bam),
        Path(snakemake.input.fname_reference),
        Path(snakemake.output.fname_result),
        Path(snakemake.output.dname_work),
    )
