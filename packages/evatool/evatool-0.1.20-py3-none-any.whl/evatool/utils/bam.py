#!/usr/bin/env python
# -*- conding:utf-8 -*-
# @AUTHOR: Gui-Yan Xie
# @CONTACT: xieguiyan at hust dot edu dot cn
# @DATE: 2021-09-08 20:10:26
# @DESCRIPTION:

from .fastq import Fastq
from .tag import Tag
import subprocess


class Bam(object):
    def __init__(self, fastq: Fastq, tag: Tag):
        self.fastq = fastq
        self.tag = tag
        self.fileprefix = f"{self.fastq.outputdir}/{self.fastq.inputfile.stem}"

    def bed_count(self):
        out_genome_sort_bed_count_handle = open(f"{self.fileprefix}.genome.sort.bed.count", "w")
        with open(f"{self.fileprefix}.genome.sort.bed", "r") as bf:
            for j in bf:
                line = j.strip().split("\t")
                # tag_name = line[3]
                tag_count = self.tag.tag_count_dict[line[3]]
                line[4] = str(tag_count)
                out_genome_sort_bed_count_handle.write("\t".join(line) + "\n")
        out_genome_sort_bed_count_handle.close()

    def bed_merge(self):
        cmd = [
            self.fastq.config.config["bedtools"],
            "merge -s -d 10 -c 6,4,5,5 -o first,collapse,sum,median -i",
            f"{self.fileprefix}.genome.sort.bed.count",
            ">",
            f"{self.fileprefix}.genome.merge.bed",
        ]
        cmd = " ".join(cmd)
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def bed_inter(self):
        cmd = [
            self.fastq.config.config["bedtools"],
            "intersect",
            "-a",
            f"{self.fileprefix}.genome.merge.bed",
            "-b",
            self.fastq.config.config["trans_bed_annotation"],
            "-wa",
            "-wb",
            ">",
            f"{self.fileprefix}.genome.annotation.info",
            "&&",
            self.fastq.config.config["bedtools"],
            "intersect",
            "-a",
            f"{self.fileprefix}.genome.merge.bed",
            "-b",
            self.fastq.config.config["trans_bed_annotation"],
            "-wa",
            "-v",
            ">",
            f"{self.fileprefix}.genome.unanno.info",
            "&&",
            self.fastq.config.config["bedtools"],
            "intersect",
            "-a",
            f"{self.fileprefix}.genome.merge.bed",
            "-b",
            self.fastq.config.config["exon_bed_annotation"],
            "-wa",
            "-wb",
            ">",
            f"{self.fileprefix}.exon.annotation.info",
        ]
        cmd = " ".join(cmd)
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def process_bam(self):
        if self.tag.tag_count_dict:
            self.bed_count()
            merge = self.bed_merge()
            if merge.returncode == 0:
                self.fastq.log.log("Successfully merge bed!")
            else:
                self.fastq.log.log("Faied to merge bed!")
            inter = self.bed_inter()
            if inter.returncode == 0:
                self.fastq.log.log("Successfully inter bed!")
            else:
                self.fastq.log.log("Faied to merge bed!")
        else:
            self.fastq.log.log(f"Failed to load {self.fileprefix}.fa!")
