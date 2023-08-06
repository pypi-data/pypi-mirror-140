#!/usr/bin/env python
# -*- conding:utf-8 -*-
# @AUTHOR: Gui-Yan Gui
# @CONTACT: xieguiyan.at.hust.dot.edu.dot.com
# @DATE: 2021-09-03 11:21:07
# @DESCRIPTION:

import sys
from pathlib import Path

# sys.path.append("../EVAtool")

from evatool.utils.fastq import Fastq
from evatool.utils.config import Config
from evatool.utils.logger import Logger
from evatool.utils.sam import SAM
from evatool.utils.bam import Bam
from evatool.utils.tag import Tag
from evatool.utils.stat import Stat
from evatool.utils.plot import Plot
from evatool.utils.report import Report

import argparse
import datetime
import logging
import logging.config

current_path = Path(__file__).parent


def run(inputfile: Path, outputdir: Path, config: Path, ncrna_lst: list) -> None:
    config = Config(config)
    logger = Logger(f"{outputdir}/evatool.log")
    # logger.info("Start pre-processing")
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Start pre-processing...")
    fastq_result = Fastq(inputfile, outputdir, config=config, log=logger, ncrna_lst=ncrna_lst)
    fastq_result.process_fastq()
    tag_result = Tag(fastq=fastq_result)
    tag_result.pocess_stat()
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Successed in pre-processing!")
    # logger.info("Start mapping...")
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Start mapping...")
    sam_result = SAM(fastq=fastq_result)
    sam_result.get_sam()
    bam_result = Bam(fastq=fastq_result, tag=tag_result)
    bam_result.process_bam()
    # logger.info("Start quantification")
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Successed in mapping!")
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Start quantification...")
    stat_result = Stat(fastq=fastq_result, tag=tag_result)
    stat_result.stat_match()
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Successed quantification!")
    return 1


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="EVAtool could be used to estimate the quantification and abundence of small ncRNA from EV or other sources.",
    )
    parser.add_argument("-i", "--input", help="The path of the input file, the file type could be '.sra, .fastq.gz or .fastq'.", required=True)
    parser.add_argument("-o", "--output", help="The path of output file.", required=True)
    parser.add_argument("-c", "--config", help="The path of the Config file. User can download the config file from url, or define yourself.", required=False, default="./resource/reference_config.json")
    parser.add_argument(
        "-n",
        "--ncrna",
        nargs="*",
        type=str,
        help="The list of small ncRNA types.  User can use default ncRNA list (miRNA, rRNA, tRNA, piRNA, snoRNA, snRNA, YRNA), or define yourself.",
        required=False,
        default=["miRNA", "rRNA", "tRNA", "piRNA", "snoRNA", "snRNA", "YRNA"],
    )
    configure = parser.parse_args()

    logging.config.fileConfig(f"{current_path}/resource/logging.conf")
    logger = logging.getLogger("EVAtool")
    log_name = logger.handlers[0].baseFilename
    logger.handlers[0].baseFilename = log_name.replace("evatool.log", f"{configure.output}/test.log")
    logger.info(f"Start processing {configure.input}")
    result = run(configure.input, configure.output, configure.config, configure.ncrna)
    if result == 1:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: start generate report")
        plot_result = Plot(configure.input, configure.output, configure.ncrna)
        plot_result.generate_plot()
        report_result = Report(configure.input, configure.output, configure.config, configure.ncrna)
        report_result.prepare_html()
        logger.info(f"Finished! The result are stored in {configure.output}!")
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Success! All results are stored in {configure.output}!")
    else:
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Failed!")
        logger.error(f"Failed in processing your data, please check the problems in the log file: {configure.output}/evatool.log")


if __name__ == "__main__":
    main()
