# **EVAtool**

---

![example](https://img.shields.io/badge/Python-%3E%203.5-orange)
![example](https://img.shields.io/badge/JAVA-JDK8-blueviolet)
![example](https://img.shields.io/pypi/v/evatool?color=blue)
![example](https://img.shields.io/badge/Docker%20build%20-automated-important)
![example](https://img.shields.io/pypi/format/wheel)
![example](https://img.shields.io/badge/numpy-%3E%3D1.15-yellow)
![example](https://img.shields.io/badge/seaborn-%3E%3D0.9.0-yellowgreen)

### Quick start
If you would like to get start using EVAtool, please following the any of the follwing document.

* [**Quick start from  PyPI**](https://pypi.org/project/evatool/)
* [**Quick start from Docker**](https://hub.docker.com/r/guobioinfolab/evatool)

### Introduction
EVAtool (EV analysis tool) is a state-of-the-art tool for quantification and abundance of small ncRNA-seq dataset in EVs. In EVAtool, we collected seven ncRNA types (miRNA, snoRNA, piRNA, snRNA, rRNA, tRNA and Y RNA) references as default to evaluate the abundence of each small ncRNA in EVs.

With current newest dependences (mainly bowtie2, samtool, fastq-dump, bedtools and trimmomatic-0.39.jar) and high-performance algorithm RDAA (Reads Dynamic Assignment Algorithm), the tool is perfectly capable of processing small RNA-seq data from small EVs (sEVs) or large EVs (lEVs). It is also capable of processing other RNA-seq data (such as long ncRNA data) with minor modifications to the command-line call. Finally, EVAtool visualized the main results and supports the online report.

EVAtool has been implemented in [Python >=3.5](#python), [Jupyter](#jupyter) and [HTML](#html).

### Table of Contents

* [System Requirements](#system-requirements)
* [Python](#python)
    * [Installation with pip](#installation-with-pip)
    * [Installation from source](#installation-from-source)
    * [Quick Start by pip](#quick-start-by-pip)
* [Docker](#docker)
    * [Installation](#installation)
    * [Quick Start by docker](#quick-start-by-docker)
* [Advanced option](#advanced-option)
* [Directory tree](#directory-tree)
* [Help](#help)

### System Requirements

* Windows (>= 7), Mac OS X (>= 10.8) or Linux
* [Python >= 3.5](https://www.python.org/downloads/)
* [JDK 8](https://www.oracle.com/java/technologies/javase/javase8-archive-downloads.html)

All other software dependencies are installed automatically when installing EVAtool. Some softwares versions are as follows:
* samtools = 1.12 <br>
* bowtie2 = 2.4.2 <br>
* fastq-dump = 2.10.9 <br>
* trimmomatic-0.39.jar <br>
* bedtools = 2.30.0 <br>

### Python

#### Installation with `pip`

The Python version of EVAtool can be installed by running the following from a terminal:

    pip install EVAtool

Installation of EVAtool and all dependencies should take no more than one minutes.

#### Installation from source

The Python version of PHATE can be installed from GitHub by running the following from a terminal:

    git clone --recursive git@github.com:xieguiyan/EVAtool.git
    cd EVAtool/
    python setup.py install --user

#### Quick Start by pip

To begin, the human genome and seven types references needed to be download from http://bioinfo.life.hust.edu.cn/EVAtool/ref/refs.zip and unzip it into the working directory.

    mkdir ~/evatool_work
    cd ~/evatool_work
    wget "http://bioinfo.life.hust.edu.cn/EVAtool/ref/refs.zip"
    unzip refs.zip

If you have already prepared the data file (SRA, FASTQ or zipped FASTQ format) you can run EVAtool as follows (Here we use example.fastq.gz data as an example):

    wget "http://bioinfo.life.hust.edu.cn/EVAtool/example/example.fastq.gz"
    evatool \
    -i example.fastq.gz
    -o {directory for output or .}


EVAtool accepts the following data types: `example.sra`, `example.fastq` and `example.fastq.gz`.

### Docker

#### Installation

The docker image of evatool can be accessed by running the following from a terminal:

    docker pull guobioinfolab/evatool

Then, prepare reference data and sequence data like the `pip` part:

    mkdir ~/evatool_work
    cd ~/evatool_work
    wget "http://bioinfo.life.hust.edu.cn/EVAtool/ref/refs.zip"
    unzip refs.zip
    wget "http://bioinfo.life.hust.edu.cn/EVAtool/example/example.fastq.gz"

#### Quick Start by docker

Take the example.fastq.gz as example:

    docker run -it -v $PWD:/work_path -w /work_path guobioinfolab/evatool -i example.fastq.gz -o .


### Advanced option
1. Custom ncRNA type(s)
    - Based on existing reference sequences
        - change the input parameter of ncRNA type list, the default ncRNAs are include 7 types: "miRNA" "rRNA" "tRNA" "piRNA" "snoRNA" "snRNA" "YRNA".
    - Add other type reference sequences
        - Three steps :

        1. Add the ncRNA reference and index into refs;

        ```
        mkdir [ncRNA name]
        add the reference and index to the directory
        ```

        2. Change the input parameter of ncRNA type list;

        ```
        -n  "miRNA" "rRNA" "tRNA"
        ```

        3. Add the ncRNA name and reference directory in config file as following the existing ways.

        ```
        "miRNA_index": "/refs/miRNA/hsa.hairpin.fa"
        ```



### Directory tree


```
├── bin
│   ├── bedtools
│   ├── bowtie2
│   ├── bowtie2-align-l
│   ├── bowtie2-align-l-debug
│   ├── bowtie2-align-s
│   ├── bowtie2-align-s-debug
│   ├── fastq-dump
│   ├── samtools
│   └── trimmomatic-0.39.jar
├── __init__.py
├── main.py
├── resource
│   ├── __init__.py
│   ├── logging.conf
│   ├── reference_config.json
│   ├── template_report.html
│   └── tool_config.json
└── utils
    ├── bam.py
    ├── config.py
    ├── fastq.py
    ├── __init__.py
    ├── logger.py
    ├── plot.py
    ├── report.py
    ├── sam.py
    ├── stat.py
    └── tag.py
```


### Help

If you have any questions or require assistance using EVAtool, please contact us: xieguiyan@hust.edu.cn. More informations and usage could be found in the [**EVAtool web**](http://bioinfo.life.hust.edu.cn/EVAtool).
