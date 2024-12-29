# GDMCv
An integrated tool for viral phage prediction using genomad and DeepMicroClass.

## Installation
### Dependencies
geNomad: https://github.com/apcamargo/genomad

DeepMicroClass: https://github.com/chengsly/DeepMicroClass

seqkit: https://github.com/shenwei356/seqkit.git

### An easiler way to install
~~~
git clone https://github.com/XiaomengWang0413/GDMCv
cd GDMCv
~~~
You can use anaconda to install the ***.yaml. 
### geNomad
~~~
conda env create -f geNomad.yaml
conda activate genomad
conda deactivate
~~~

### DeepMicroClass
~~~
conda env create -f DeepMicroClass.yaml
conda activate DeepMicroClass
conda deactivate
~~~

### seqkit
~~~
conda env create -f seqkit.yaml
conda activate seqkit
conda deactivate
~~~

## databases
~~~
cd GDMCv/database
genomad download-database .
~~~

## Usage

~~~
usage: python GDMCv.py [-h] [-i INPUT] [-o OUTPUT] [-t THREADS] [-l LENGTH] [-v]

Run geNomad and DeepMicroClass pipeline for viral sequence prediction and extraction.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file (FASTA format)
  -o OUTPUT, --output OUTPUT
                        Output folder name
  -t THREADS, --threads THREADS
                        Number of CPU cores to use (default: 8)
  -l LENGTH, --length LENGTH
                        Minimum sequence length for filtering (default: 2000bp)
  -v, --version         Show script version information
~~~
## example
~~~
gunzip test.fasta.gz
python GDMCv.py -i test.fasta -l 5000 -o test
~~~

## Reference
~~~
1. Camargo, A. P., Roux, S., Schulz, F., Babinski, M., Xu, Y., Hu, B., Chain, P. S. G., Nayfach, S., & Kyrpides, N. C. — Nature Biotechnology (2023), DOI: 10.1038/s41587-023-01953-y.

2. Shengwei Hou, Tianqi Tang, Siliangyu Cheng, Yuanhao Liu, Tian Xia, Ting Chen, Jed A Fuhrman, Fengzhu Sun, DeepMicroClass sorts metagenomic contigs into prokaryotes, eukaryotes and viruses, NAR Genomics and Bioinformatics, Volume 6, Issue 2, June 2024, lqae044, https://doi.org/10.1093/nargab/lqae044.

3. Wei Shen*, Botond Sipos, and Liuyang Zhao. 2024. SeqKit2: A Swiss Army Knife for Sequence and Alignment Processing. iMeta e191. doi:10.1002/imt2.191.
~~~

