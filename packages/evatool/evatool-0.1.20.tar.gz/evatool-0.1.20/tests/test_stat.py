import sys
from pathlib import Path

sys.path.append("../EVAtool")


def test_stat():
    """Test stat.py"""
    from evatool.utils.stat import Stat
    from evatool.utils.config import Config
    from evatool.utils.logger import Logger
    from evatool.utils.fastq import Fastq
    from evatool.utils.tag import Tag

    stat = Stat(
        fastq=Fastq(
            inputfile="/workspace/xiegy/EVAtool/data/srr_for_test/SRR6831610_1.fastq.gz",
            outputdir="/workspace/xiegy/EVAtool/tmp_result/01_high_ratio_yrna_result",
            config=Config(configfile="/home/xiegy/github/EVAtool/refs/reference_config.json"),
            log=Logger(),
            ncrna_lst=["miRNA", "rRNA", "tRNA", "piRNA", "snoRNA", "snRNA", "YRNA"],
        ),
        tag=Tag(
            fastq=Fastq(
                inputfile="/workspace/xiegy/EVAtool/data/srr_for_test/SRR6831610_1.fastq.gz",
                outputdir="/workspace/xiegy/EVAtool/tmp_result/01_high_ratio_yrna_result",
                config=Config(configfile="/home/xiegy/github/EVAtool/refs/reference_config.json"),
                log=Logger(),
                ncrna_lst=["miRNA", "rRNA", "tRNA", "piRNA", "snoRNA", "snRNA", "YRNA"],
            )
        ),
    )
    stat.stat_match()


test_stat()
