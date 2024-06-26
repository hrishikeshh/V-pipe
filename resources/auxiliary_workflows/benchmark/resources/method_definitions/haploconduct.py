# GROUP: global
# CONDA: haploconduct = 0.2.1
# CONDA: samtools = 1.15.1
# CONDA: pysam = 0.19.1
# CONDA: biopython = 1.76

import statistics
import subprocess
from pathlib import Path

import pysam
from Bio import SeqIO


def main(
    fname_bam,
    fname_reference,
    fname_result,
    fname_status,
    dname_work,
    timeout_sec,
    thread_num,
):
    dname_work.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "samtools",
            "fastq",
            "-1",
            dname_work / "reads.R1.fastq",
            "-2",
            dname_work / "reads.R2.fastq",
            fname_bam,
        ],
        check=True,
    )

    # estimate reasonable split parameter
    # goal: 500 < coverage/split_num < 1000
    depth_list = []
    for line in pysam.depth("-a", str(fname_bam)).splitlines():
        _, _, depth = line.split()
        depth_list.append(int(depth))
    coverage_mean = statistics.mean(depth_list)

    split_num = 1
    while coverage_mean / split_num > 1000:
        split_num += 1
    print(
        f"Split estimate: {split_num} (coverage / split_num = {round(coverage_mean / split_num, 1)})"
    )

    try:
        subprocess.run(
            [
                "haploconduct",
                "savage",
                "--ref",
                fname_reference.resolve(),
                "--num_threads",
                str(thread_num),
                "--split",
                str(split_num),
                "-p1",
                (dname_work / "reads.R1.fastq").resolve(),
                "-p2",
                (dname_work / "reads.R2.fastq").resolve(),
            ],
            cwd=dname_work,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired:
        print(f"Method timeout after {timeout_sec} seconds")
        fname_status.write_text("timeout")
        fname_result.touch()
        return

    # select result (later stage is better)
    result_a = dname_work / "contigs_stage_a.fasta"
    result_b = dname_work / "contigs_stage_b.fasta"
    result_c = dname_work / "contigs_stage_c.fasta"

    for result in [result_c, result_b, result_a]:
        if result.exists():
            print(f"Using stage result {result}")

            # add dummy frequencies
            record_list = []
            for record in SeqIO.parse(result, "fasta"):
                record.description = "freq:-1"
                record_list.append(record)
            SeqIO.write(record_list, fname_result, "fasta")

            break
    else:
        fname_status.write_text("crash")
        fname_result.touch()


if __name__ == "__main__":
    main(
        Path(snakemake.input.fname_bam),
        Path(snakemake.input.fname_reference),
        Path(snakemake.output.fname_result),
        Path(snakemake.output.fname_status),
        Path(snakemake.output.dname_work),
        (snakemake.resources.time_min - 60) * 60,  # one hour for setup
        snakemake.threads,
    )
