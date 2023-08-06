#!/usr/bin/env python
# -*- conding:utf-8 -*-
# @AUTHOR: Gui-Yan Xie
# @CONTACT: xieguiyan at hust dot edu dot cn
# @DATE: 2021-09-26 11:06:09
# @DESCRIPTION:

from .fastq import Fastq
import subprocess
from pathlib import Path
from multiprocessing import Pool, cpu_count


class SAM(object):
    def __init__(self, fastq: Fastq):
        self.fastq = fastq
        self.samdir = Path(fastq.inputfile)
        self.tag_fa = f"{self.fastq.outputdir}/{self.fastq.inputfile.stem}.fa"
        self.ncrna_lst = ["miRNA", "rRNA", "tRNA", "piRNA", "snoRNA", "snRNA", "YRNA"]

    def mapped_genome_anno(self) -> None:
        outputpre = f"{self.fastq.outputdir}/{self.fastq.inputfile.stem}"
        cmd = [
            self.fastq.config.config["bowtie"],
            "-x",
            self.fastq.config.config["genome_index"],
            "-p",
            self.fastq.config.config["cpu_number"],
            self.fastq.config.config["bowtie_para_4_genome"],
            "-f",
            self.tag_fa,
            "-S",
            f"{outputpre}.genome.sam",
            "2>",
            f"{outputpre}.genome.bowtie.stat",
            "&&",
            self.fastq.config.config["samtools"],
            "view -bS",
            f"{outputpre}.genome.sam",
            ">",
            f"{outputpre}.genome.bam",
            "&&",
            self.fastq.config.config["samtools"],
            "sort",
            f"{outputpre}.genome.bam",
            "-o",
            f"{outputpre}.genome.sort.bam",
            "&&",
            self.fastq.config.config["bedtools"],
            "bamtobed -i",
            f"{outputpre}.genome.sort.bam",
            ">",
            f"{outputpre}.genome.sort.bed",
        ]
        cmd = " ".join(cmd)
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def ncRNA_map(self, ncrna) -> None:
        sample_input = self.fastq.inputfile.stem
        cmd = [
            self.fastq.config.config["bowtie"],
            "-x",
            self.fastq.config.config[ncrna + "_index"],
            "-p",
            self.fastq.config.config["cpu_number"],
            self.fastq.config.config[f"bowtie_para_4_{ncrna}"],
            "-f",
            self.tag_fa,
            "-S",
            f"{self.fastq.outputdir}/{sample_input}.{ncrna}.sam",
            "2>",
            f"{self.fastq.outputdir}/{sample_input}.{ncrna}.bowtie.stat",
        ]
        cmd = " ".join(cmd)
        map_result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if map_result.returncode == 0:
            self.fastq.log.log(f"Sucess in align to {ncrna} reference!")
        else:
            self.fastq.log.log(f"Failed in align to {ncrna} reference!")

    def get_sam(self) -> None:
        genome_map = self.mapped_genome_anno()
        if genome_map.returncode == 0:
            self.fastq.log.log("Success in align to genome reference!")
        else:
            self.fastq.log.log("Failed in align to genome reference!")
        p = Pool(cpu_count())
        for ncrna in self.ncrna_lst:
            p.apply_async(self.ncRNA_map, args=(ncrna,))
        p.close()
        p.join()
