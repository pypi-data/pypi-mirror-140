import sys
from pathlib import Path

sys.path.append("../EVAtool")


def test_plot():
    """Test plot.py"""
    from evatool.utils.plot import Plot

    plot_result = Plot(inputfile="/home/xiegy/github/EVAtool/test/example-data/example.fastq.gz", outputdir="/home/xiegy/github/EVAtool/test/tmp_result/example_fq_gz", ncrna_lst=["miRNA", "rRNA", "tRNA", "piRNA", "snoRNA", "snRNA", "YRNA"])
    plot_result.generate_plot()


test_plot()
