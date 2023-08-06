import sys
from pathlib import Path

sys.path.append("../EVAtool")


def test_sam():
    """Test sam.py"""
    from evatool.utils.sam import SAM
    from evatool.utils.config import Config
    from evatool.utils.logger import Logger
    from evatool.utils.fastq import Fastq

    sam = SAM(
        fastq=Fastq(
            inputfile="/home/xiegy/github/EVAtool/test/example-data/example.fastq.gz",
            outputdir="/home/xiegy/github/EVAtool/test/tmp_result/example_fq_gz",
            config=Config(configfile="/home/xiegy/github/EVAtool/refs/reference_config.json"),
            log=Logger(),
        )
    )
    sam.get_sam()


test_sam()
