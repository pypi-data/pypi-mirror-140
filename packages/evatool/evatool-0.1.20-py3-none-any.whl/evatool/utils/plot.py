#!/usr/bin/env python
# -*- conding:utf-8 -*-
# @AUTHOR: Gui-Yan Xie
# @CONTACT: xieguiyan at hust dot edu dot cn
# @DATE: 2021-11-19 11:28:17
# @DESCRIPTION:
# FILE: plot.py

import matplotlib
import seaborn as sns
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
from pathlib import Path

sns.set()
plt.switch_backend("agg")


class Plot:
    def __init__(self, inputfile: Path, outputdir: Path, ncrna_lst: list = ["miRNA", "rRNA", "tRNA", "piRNA", "snoRNA", "snRNA", "YRNA"]):
        self.inputfile = Path(inputfile)
        self.outputdir = outputdir
        self.ncrna_lst = ncrna_lst
        self.samprefix = f"{self.outputdir}/{self.inputfile.stem}"

    def read_length_distribution(self) -> None:
        # Reads length distribution
        sns.set_style("white")
        plt.figure(dpi=300, figsize=(9, 5))
        read = pd.read_table(f"{self.samprefix}.freq.stat", sep="\t", header=None, skipfooter=1, engine="python")
        read.columns = ["Read length", "count", "Read count percentage"]
        read_len = sns.lineplot(x="Read length", y="Read count percentage", data=read)
        sns.despine()
        # save image
        read_len.get_figure().savefig(f"{self.outputdir}/distribution_of_read_len.png", bbox_inches="tight")
        read_len.get_figure().savefig(f"{self.outputdir}/distribution_of_read_len.pdf", bbox_inches="tight")

    def read_type_distribution_hist(self) -> None:
        # Read type distribution
        sns.set_style("white")
        plt.figure(dpi=300, figsize=(9, 5))
        ncrna_type = pd.read_table(f"{self.samprefix}.stat", header=None, sep="\t", skiprows=4, dtype=str)
        ncrna_type.columns = ["Category", "MappingTag", "Ratio"]
        ncrna_type["Ratio"] = ncrna_type["Ratio"].apply(lambda x: np.nan if x in ["-"] else x[:-1]).astype(float) / 100
        read_type = sns.barplot(x="Category", y="Ratio", data=ncrna_type)
        read_type.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=1))
        sns.despine()
        # save image
        read_type.get_figure().savefig(f"{self.outputdir}/distribution_of_ncRNA_type.png")
        read_type.get_figure().savefig(f"{self.outputdir}/distribution_of_ncRNA_type.pdf")

    def read_type_distribution_pie(self) -> None:
        plt.figure(dpi=300, figsize=(8, 8))
        read_type_pie = pd.read_table(f"{self.samprefix}.stat", header=None, sep="\t", skiprows=4, dtype=str)
        read_type_pie.columns = ["Category", "MappingTag", "Ratio"]
        read_type_pie["Ratio"] = read_type_pie["Ratio"].apply(lambda x: np.nan if x in ["-"] else x[:-1]).astype(float)
        read_type_map = pd.read_table(f"{self.samprefix}.stat", header=None, sep=":", skiprows=1, dtype=str)
        unmap_ratio = list(re.findall(r"\((.*)%\)", read_type_map[0:2][1][1]))
        unmap_ratio_f = [float(i) for i in unmap_ratio]
        all_ratio = list(read_type_pie["Ratio"]) + [(100 - sum(list(read_type_pie["Ratio"])))]
        all_category = list(read_type_pie["Category"]) + ["other"]
        all_labels = ["{0} - {1:1.2f}%".format(i, j) for i, j in zip(all_category, all_ratio)]
        plt.pie(all_ratio)
        plt.legend(labels=all_labels, bbox_to_anchor=(1.05, 0.5), loc="center", frameon=False, fontsize=7)
        # save image
        plt.savefig(f"{self.outputdir}/distribution_of_ncRNA_type_pie.png")
        plt.savefig(f"{self.outputdir}/distribution_of_ncRNA_type_pie.pdf")

    def exp_distribution_bar(self) -> None:
        for i in self.ncrna_lst:
            plt.figure(dpi=300, figsize=(8, 8))
            read_expr = pd.read_table(f"{self.samprefix}.{i}.exp")
            plt.suptitle(f"The expression distribution of {i}")
            sns.set_style("white")
            # RPM high level
            plt.subplot(2, 2, 1)
            plt.hist(read_expr["RPM"], alpha=0.3, color="#BEA6A1")
            sns.rugplot(read_expr["RPM"], color="#00787C")
            sns.despine()
            plt.ylabel(f"The number of quantified {i}")
            # RPM hist
            plt.subplot(2, 2, 2)
            plt.hist(read_expr["RPM"], bins=40, facecolor="#EA6856")
            plt.xlabel("RPM")
            # TagCount
            plt.subplot(2, 2, 3)
            plt.hist(read_expr["TagCount"], alpha=0.3, color="#00ADB1")
            sns.rugplot(read_expr["TagCount"], color="#A15043")
            sns.despine()
            plt.ylabel(f"The number of quantified {i}")
            # TagCount hist
            plt.subplot(2, 2, 4)
            plt.hist(read_expr["TagCount"], bins=40, facecolor="#00C9D3")
            sns.despine()
            plt.xlabel("TagCount")
            plt.savefig(f"{self.outputdir}/exp_distribution_of_{i}.png")
            plt.savefig(f"{self.outputdir}/exp_distribution_of_{i}.pdf")
        matplotlib.rc("figure", max_open_warning=0)

    def number_of_rna_line(self) -> None:
        rna_count = []
        for i in self.ncrna_lst:
            count = len(open(f"{self.samprefix}.{i}.exp", "r").readlines()) - 1
            rna_count.append(count)
        plt.figure(dpi=300, figsize=(8, 5))
        plt.plot(self.ncrna_lst, rna_count, "r", lw=2, color="#EA6856")
        sns.despine()
        plt.xlabel("ncRNA type")
        plt.ylabel("The number of identifed RNAs")
        # save image
        plt.savefig(f"{self.outputdir}/distribution_of_ncRNA_number_line.png")
        plt.savefig(f"{self.outputdir}/distribution_of_ncRNA_number_line.pdf")

    def generate_plot(self):
        self.read_length_distribution()
        self.read_type_distribution_hist()
        self.read_type_distribution_pie()
        self.exp_distribution_bar()
        self.number_of_rna_line()
