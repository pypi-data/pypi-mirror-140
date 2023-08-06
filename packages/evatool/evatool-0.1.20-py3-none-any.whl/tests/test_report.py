import sys
from pathlib import Path

sys.path.append("../EVAtool")


def test_report():
    """Test report.y"""
    from evatool.utils.report import Report

    report_html = Report(
        inputfile="/home/xiegy/github/EVAtool/test/example-data/example.fastq.gz",
        outputdir="/home/xiegy/github/EVAtool/test/tmp_result/example_fq_gz",
        config="/home/xiegy/github/EVAtool/refs/reference_config.json",
        ncrna_list=["miRNA", "rRNA", "tRNA", "piRNA", "snoRNA", "snRNA", "YRNA"],
    )
    report_html.prepare_html()


test_report()
