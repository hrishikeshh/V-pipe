<!-- markdownlint-disable MD013 MD041 -->
<picture>
  <source
    media="(prefers-color-scheme: light)"  
    srcset="https://cbg-ethz.github.io/V-pipe/assets/img/logo-vpipe.svg">
  <source
    media="(prefers-color-scheme: dark)"  
    srcset="https://cbg-ethz.github.io/V-pipe/assets/img/logo-vpipe-dark.svg">
  <img alt="Logo" src="https://cbg-ethz.github.io/V-pipe/assets/img/logo-vpipe.svg" width="50%" />
</picture>

[![bio.tools](https://img.shields.io/badge/bio-tools-blue.svg)](https://bio.tools/V-Pipe)
[![Snakemake](https://img.shields.io/badge/snakemake-≥7.11.0-blue.svg)](https://snakemake.github.io/snakemake-workflow-catalog/?usage=cbg-ethz/V-pipe)
[![Deploy Docker image](https://github.com/cbg-ethz/V-pipe/actions/workflows/deploy-docker.yaml/badge.svg)](https://github.com/cbg-ethz/V-pipe/pkgs/container/v-pipe)
[![Tests](https://github.com/cbg-ethz/V-pipe/actions/workflows/run_regression_tests.yaml/badge.svg)](https://github.com/cbg-ethz/V-pipe/actions/workflows/run_regression_tests.yaml)
[![Mega-Linter](https://github.com/cbg-ethz/V-pipe/actions/workflows/mega-linter.yml/badge.svg)](https://github.com/cbg-ethz/V-pipe/actions/workflows/mega-linter.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

V-pipe is a workflow designed for the analysis of next generation sequencing (NGS) data from viral pathogens. It produces a number of results in a curated format (e.g., consensus sequences, SNV calls, local/global haplotypes).
V-pipe is written using the Snakemake workflow management system.

## Usage

Different ways of initializing V-pipe are presented below. We strongly encourage you to deploy it [using the quick install script](#using-quick-install-script), as this is our preferred method.

To configure V-pipe refer to the documentation present in [config/README.md](config/README.md).

V-pipe expects the input samples to be organized in a [two-level](config/README.md#samples) directory hierarchy,
and the sequencing reads must be provided in a sub-folder named `raw_data`. Further details can be found on the [website](https://cbg-ethz.github.io/V-pipe/usage/).
Check the utils subdirectory for [mass-importers tools](utils/README.md#samples-mass-importers) that can assist you in generating this hierarchy.

We provide [virus-specific base configuration files](config/README.md#virus-base-config) which contain handy defaults for, e.g., HIV and SARS-CoV-2. Set the virus in the general section of the configuration file:

```yaml
general:
  virus_base_config: hiv
```

Also see [snakemake's documentation](https://snakemake.readthedocs.io/en/stable/executing/cli.html) to learn more about the command-line options available when executing the workflow.


### Tutorials

Tutorials for your first steps with V-pipe for different scenarios are available in the [docs/](docs/README.md) subdirectory.


### Using quick install script

To deploy V-pipe, use the [installation script](utils/README.md#quick-installer) with the following parameters:

```bash
curl -O 'https://raw.githubusercontent.com/cbg-ethz/V-pipe/master/utils/quick_install.sh'
./quick_install.sh -w work
```

This script will download and install miniconda, checkout the V-pipe git repository (use `-b` to specify which branch/tag) and setup a work directory (specified with `-w`) with an executable script that will execute the workflow:

```bash
cd work
# edit config.yaml and provide samples/ directory
./vpipe --jobs 4 --printshellcmds --dry-run
```

Test data to test your installation is available with the tutorials provided in the [docs/](docs/README.md) subdirectory.

### Using Docker

Note: the [docker image](https://github.com/cbg-ethz/V-pipe/pkgs/container/v-pipe) is only setup with components to run the workflow for HIV and SARS-CoV-2 virus base configurations.
Using V-pipe with other viruses or configurations might require internet connectivity for additional software components.

Create `config.yaml` or `vpipe.config` and then populate the `samples/` directory.
For example, the following config file could be used:

```yaml
general:
  virus_base_config: hiv

output:
  snv: true
  local: true
  global: false
  visualization: true
  QA: true
```

Then execute:

```bash
docker run --rm -it -v $PWD:/work ghcr.io/cbg-ethz/v-pipe:master --jobs 4 --printshellcmds --dry-run
```

### Using Snakedeploy

First install [mamba](https://github.com/conda-forge/miniforge#mambaforge), then create and activate an environment with Snakemake and Snakedeploy:

```bash
mamba create -c conda-forge -c bioconda --name snakemake snakemake snakedeploy
conda activate snakemake
```

Snakemake's [official workflow installer Snakedeploy](https://snakemake.github.io/snakemake-workflow-catalog/?usage=cbg-ethz/V-pipe) can now be used:

```bash
snakedeploy deploy-workflow https://github.com/cbg-ethz/V-pipe --tag master .
# edit config/config.yaml and provide samples/ directory
snakemake --use-conda --jobs 4 --printshellcmds --dry-run
```

## Dependencies

- **[Conda](https://conda.io/docs/index.html)**

  Conda is a cross-platform package management system and an environment manager application. Snakemake uses mamba as a package manager.

- **[Snakemake](https://snakemake.readthedocs.io/)**

  Snakemake is the central workflow and dependency manager of V-pipe. It determines the order in which individual tools are invoked and checks that programs do not exit unexpectedly.

- **[VICUNA](https://www.broadinstitute.org/viral-genomics/vicuna)**

  VICUNA is a _de novo_ assembly software designed for populations with high mutation rates. It is used to build an initial reference for mapping reads with ngshmmalign aligner when a `references/cohort_consensus.fasta` file is not provided. Further details can be found in the [wiki](https://github.com/cbg-ethz/V-pipe/wiki/getting-started#input-files) pages.

### Computational tools

Other dependencies are managed by using isolated conda environments per rule, and below we list some of the computational tools integrated in V-pipe:

- **[FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)**

  FastQC gives an overview of the raw sequencing data. Flowcells that have been overloaded or otherwise fail during sequencing can easily be determined with FastQC.

- **[PRINSEQ](http://prinseq.sourceforge.net/)**

  Trimming and clipping of reads is performed by PRINSEQ. It is currently the most versatile raw read processor with many customization options.

- **[ngshmmalign](https://github.com/cbg-ethz/ngshmmalign)**

  We perform the alignment of the curated NGS data using our custom ngshmmalign that takes structural variants into account. It produces multiple consensus sequences that include either majority bases or ambiguous bases.

- **[bwa](https://github.com/lh3/bwa)**

  In order to detect specific cross-contaminations with other probes, the Burrows-Wheeler aligner is used. It quickly yields estimates for foreign genomic material in an experiment.
  Additionally, It can be used as an alternative aligner to ngshmmalign.

- **[MAFFT](http://mafft.cbrc.jp/alignment/software/)**

  To standardise multiple samples to the same reference genome (say HXB2 for HIV-1), the multiple sequence aligner MAFFT is employed. The multiple sequence alignment helps in determining regions of low conservation and thus makes standardisation of alignments more robust.

- **[Samtools and bcftools](https://www.htslib.org/)**

  The Swiss Army knife of alignment postprocessing and diagnostics. bcftools is also used to generate consensus sequence with indels.

- **[SmallGenomeUtilities](https://github.com/cbg-ethz/smallgenomeutilities)**

  We perform genomic liftovers to standardised reference genomes using our in-house developed python library of utilities for rewriting alignments.

- **[ShoRAH](https://github.com/cbg-ethz/shorah)**

  ShoRAh performs SNV calling and local haplotype reconstruction by using bayesian clustering.

- **[LoFreq](https://csb5.github.io/lofreq/)**

  LoFreq (version 2) is SNVs and indels caller from next-generation sequencing data, and can be used as an alternative engine for SNV calling.

- **[SAVAGE](https://bitbucket.org/jbaaijens/savage) and [Haploclique](https://github.com/cbg-ethz/haploclique)**

  We use HaploClique or SAVAGE to perform global haplotype reconstruction for heterogeneous viral populations by using an overlap graph.

## Citation

If you use this software in your research, please cite:

Fuhrmann, L., Jablonski, K. P., Topolsky, I., Batavia, A. A., Borgsmueller, N., Icer Baykal, P., Carrara, M. ... & Beerenwinkel, (2023).
"V-Pipe 3.0: A Sustainable Pipeline for Within-Sample Viral Genetic Diversity Estimation."
_bioRxiv_, doi:[10.1101/2023.10.16.562462](https://doi.org/10.1101/2023.10.16.562462).

## Contributions

- [Ivan Topolsky\* ![orcid]](https://orcid.org/0000-0002-7561-0810), [![github]](https://github.com/dryak)
- [Pelin Icer Baykal ![orcid]](https://orcid.org/0000-0002-9542-5292), [![github]](https://github.com/picerbaykal)
- [Auguste Rimaite ![orcid]](https://orcid.org/0009-0004-6840-1668), [![github]](https://github.com/AugusteRi)
- [Lara Fuhrmann ![orcid]](https://orcid.org/0000-0001-6405-0654), [![github]](https://github.com/LaraFuhrmann)
- [Uwe Schmitt ![orcid]](https://orcid.org/0000-0002-4658-0616), [![github]](https://github.com/uweschmitt)
- [Michal Okoniewski ![orcid]](https://orcid.org/0000-0003-4722-4506), [![github]](https://github.com/michalogit)
- [Monica Dragan ![orcid]](https://orcid.org/0000-0002-7719-5892), [![github]](https://github.com/monicadragan)
- [Kim Philipp Jablonski\*\*\* ![orcid]](https://orcid.org/0000-0002-4166-4343), [![github]](https://github.com/kpj)
- [Susana Posada Céspedes\*\*\* ![orcid]](https://orcid.org/0000-0002-7459-8186), [![github]](https://github.com/sposadac)
- [David Seifert\*\*\* ![orcid]](https://orcid.org/0000-0003-4739-5110), [![github]](https://github.com/SoapZA)
- Tobias Marschall\*\*\*
- [Niko Beerenwinkel\*\* ![orcid]](https://orcid.org/0000-0002-0573-6119)

\* software maintainer ;
\** group leader ;
\*\*\* group alumni and former contributors.

[github]: https://cbg-ethz.github.io/V-pipe/assets/img/icon-github.svg
[orcid]: https://cbg-ethz.github.io/V-pipe/assets/img/icon-ORICID.svg

## Contact

We encourage users to use the [issue tracker](https://github.com/cbg-ethz/V-pipe/issues). For further enquiries, you can also contact the V-pipe Dev Team <v-pipe@bsse.ethz.ch>.
