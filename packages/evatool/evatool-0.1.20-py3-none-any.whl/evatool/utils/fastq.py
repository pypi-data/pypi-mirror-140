#!/usr/bin/env python
# -*- conding:utf-8 -*-
# @AUTHOR: Gui-Yan Xie
# @CONTACT: xieguiyan.at dot hust dot edu dot cn
# @DATE: 2021-09-03 11:46:34
# @DESCRIPTION:

from pathlib import Path
import subprocess

from .config import Config
from .logger import Logger


class Fastq(object):
    def __init__(self, inputfile: Path, outputdir: Path, config: Config, log: Logger, ncrna_lst: list = ["miRNA", "rRNA", "tRNA", "piRNA", "snoRNA", "snRNA", "YRNA"]):
        self.inputfile = Path(inputfile)
        self.outputdir = outputdir
        self.config = config
        self.log = log
        self.ncrna_lst = ncrna_lst
        self.trimname = f"{self.inputfile.stem}.fastq.trimmed.gz"

    def is_sra(self):
        return True if self.inputfile.suffix == ".sra" else False

    def is_fastq(self):
        return True if (self.inputfile.suffix == ".fastq" or self.inputfile.suffix == ".fq" or "".join(self.inputfile.suffixes) == ".fastq.gz" or "".join(self.inputfile.suffixes) == ".fq.gz") else False

    def dump_fastq(self):
        cmd = [self.config.config["fastqdump"], "--dumpbase", "--gzip", "--split-files", "-O", self.outputdir, self.inputfile]
        return subprocess.run(cmd)

    def trim(self, fq_file) -> None:
        trimmed_fq = f"{self.outputdir}/{self.trimname}"
        filter_params = f"ILLUMINACLIP:{self.config.config['adp_path']}:{self.config.config['trimmomatic_sRNA_para']}"
        cmd = f"java -jar -Xms8000m -Xmx8000m {self.config.config['trimmomatic']} SE -threads {self.config.config['cpu_number']} {fq_file} {trimmed_fq} {filter_params}"
        return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

    def process_fastq(self):
        if self.is_sra():
            rc = self.dump_fastq()
            if rc.returncode == 0:
                fq_file = f"{self.outputdir}/{self.inputfile.stem}_1.fastq.gz"
                runtrim = self.trim(fq_file)
                if runtrim.returncode == 0:
                    self.log.log(message=f"Success in trimm {self.inputfile.stem} fastq file")
                else:
                    self.log.log(message=f"Error in trimm {self.inputfile.stem} fastq file")
                self.log.log(message=f"Success in dump SRA file {self.inputfile.stem} to fastq")
            else:
                self.log.log(message=f"Error in dump SRA file {self.inputfile.stem} to fastq")
        elif self.is_fastq():
            fq_file = self.inputfile
            runtrim = self.trim(fq_file)
            if runtrim.returncode == 0:
                self.log.log(message=f"Success in trimm {self.inputfile.stem} fastq file")
            else:
                self.log.log(message=f"Error in trimm {self.inputfile.stem} fastq file")
