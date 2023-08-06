#!/usr/bin/env python
# -*- conding:utf-8 -*-
# @AUTHOR: Gui-Yan Xie
# @CONTACT: xieguiyan at hust dot edu dot cn
# @DATE: 2021-11-18 15:36:19
# @DESCRIPTION:

from jinja2 import Environment, FileSystemLoader
import datetime
from pathlib import Path

current_path = Path(__file__).parent
template_path = f"{current_path}/../resource"


class Report:
    def __init__(self, inputfile: Path, outputdir: Path, config: Path, ncrna_list: list):
        self.inputfile = Path(inputfile)
        self.outputdir = outputdir
        self.config = config
        self.ncrna_list = ncrna_list
        self.samprefix = f"{self.outputdir}/{self.inputfile.stem}"

    def generate_html(self, body, body2, num_rnas, all_top10, stoptime, img_path, config, sam_info):
        env = Environment(loader=FileSystemLoader(template_path))
        template = env.get_template("template_report.html")
        with open(f"{self.outputdir}/Report_result.html", "w+") as fout:
            html_content = template.render(stop_time=stoptime, body=body, body2=body2, num_rnas=num_rnas, all_top10=all_top10, img_path=img_path, config=config, sam_info=sam_info)
            fout.write(html_content)

    def load_readlen_data(self):
        len_dis = {}
        with open(f"{self.samprefix}.freq.stat", "r") as freg:
            for i in freg:
                if i.startswith("ok"):
                    len_stat = i.strip().split("\t")
                    len_dis["fi"] = len_stat[1]
                    len_dis["thr"] = len_stat[2]
                    len_dis["fo"] = len_stat[3]
                    len_dis["fif"] = len_stat[4]
                    len_dis["out_reads"] = len_stat[5]
                    len_dis["ratio"] = len_stat[6]
                    len_dis["total"] = len_stat[7]
        return len_dis

    def load_ncrnatype_data(self):
        map_info = {}
        all_map_info = []
        with open(f"{self.samprefix}.stat", "r") as type_freg:
            for t in type_freg:
                if t.startswith("#"):
                    anno_map_info = t.strip("#|\n").split(":")
                    map_info[anno_map_info[0]] = anno_map_info[1]
                else:
                    ncrna_stat = t.strip().split("\t")
                    if ncrna_stat[0] != "Category":
                        ncrna_dis = {}
                        ncrna_dis["Category"] = ncrna_stat[0]
                        ncrna_dis["MappedTag"] = ncrna_stat[1]
                        ncrna_dis["Ratio"] = ncrna_stat[2]
                        all_map_info.append(ncrna_dis)
        return all_map_info

    def load_num_rnas_info(self):
        rna_count = {}
        for i in self.ncrna_list:
            count = len(open(f"{self.samprefix}.{i}.exp", "r").readlines()) - 1
            rna_count[i] = count
        return rna_count

    def load_top10_rna(self):
        all_top10_info = []
        for i in self.ncrna_list:
            with open(f"{self.samprefix}.{i}.exp", "r") as exp_rna:
                a = 0
                for t in exp_rna:
                    if a < 6:
                        a = a + 1
                        line = t.strip().split("\t")
                        if line[0] != "GeneSymbol":
                            ncrna_exp = {}
                            ncrna_exp["rna"] = line[0]
                            ncrna_exp["count"] = line[1]
                            ncrna_exp["rpm"] = line[2]
                            ncrna_exp["type"] = i
                            all_top10_info.append(ncrna_exp)
                    else:
                        break
        return all_top10_info

    def load_imgpath_info(self):
        img_path = {}
        img_path["read_len"] = "distribution_of_read_len.png"
        img_path["ncrna_type"] = "distribution_of_ncRNA_type.png"
        img_path["ncrna_number"] = "distribution_of_ncRNA_number_line.png"
        img_path["ncrna_type_pie"] = "distribution_of_ncRNA_type_pie.png"
        # for i in self.ncrna_list:
        #     img_path[i] = f"exp_distribution_of_{i}.png"
        return img_path

    def prepare_html(self):
        body = []
        body2 = []
        sam_info = {}
        len_dis = self.load_readlen_data()
        num_rnas = self.load_num_rnas_info()
        all_map_info = self.load_ncrnatype_data()
        all_top10 = self.load_top10_rna()
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body.append(len_dis)
        body2 = all_map_info
        sam_info["sam_name"] = self.inputfile.stem
        sam_info["sam_path"] = self.outputdir
        sam_info["ncrna_list"] = self.ncrna_list
        img_path = self.load_imgpath_info()
        self.generate_html(body, body2, num_rnas, all_top10, time, img_path, self.config, sam_info)
