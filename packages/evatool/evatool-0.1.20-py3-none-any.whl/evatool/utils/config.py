#!/usr/bin/env python
# -*- conding:utf-8 -*-
# @AUTHOR: Gui-Yan Xie
# @CONTACT: xieguiyan.at.hust.edu.cn
# @DATE: 2021-09-03 15:29:17
# @DESCRIPTION:


import json
from pathlib import Path

current_path = Path(__file__).parent


class Config(object):
    def __init__(self, configfile: Path):
        self.configfile = Path(configfile)
        self.tool_config = Path(f"{current_path}/../resource/tool_config.json")
        self.config = self.read_config()
        self.mature_miRNA, self.hairpin_info = self.deal_mir_info()

    def read_config(self):
        with open(self.tool_config, "r") as t:
            tool_conf = json.load(t)
            for k in tool_conf:
                if tool_conf[k].startswith("./bin"):
                    tool_conf[k] = f"{current_path}/{tool_conf[k].replace('./', '../')}"
        try:
            if self.configfile.parent == Path("resource"):
                with open(f"{current_path}/../{self.configfile}", "r") as f:
                    ref_config = json.load(f)
                    for key in ref_config:
                        if ref_config[key].startswith("/refs"):
                            ref_config[key] = f"{ref_config[key].replace('/refs', './refs')}"
                        tool_conf[key] = ref_config[key]
            else:
                with open(self.configfile, "r") as f:
                    ref_config = json.load(f)
                    for key in ref_config:
                        if ref_config[key].startswith("/refs"):
                            ref_config[key] = f"{self.configfile.parent}/{ref_config[key].replace('/refs/','')}"
                        tool_conf[key] = ref_config[key]
            return tool_conf
        except IOError:
            print(f"{self.configfile} not exists.")

    def deal_mir_info(self):
        mature_miRNA = {}
        hairpin_info = {}
        with open(self.config["mirbase"], "r") as f:
            for i in f:
                line = i.strip().split("\t")
                hairpin_seq = line[4]
                mir_seq = line[3]
                miRNA_start = hairpin_seq.find(mir_seq)
                if miRNA_start == -1:
                    continue
                miRNA_len = len(mir_seq)
                hairpin_len = len(hairpin_seq)
                arm = "5p" if hairpin_len > 2 * miRNA_start + miRNA_len - 1 else "3p"
                mature_miRNA.setdefault(line[1], {})[arm] = [line[0], miRNA_start, miRNA_len, mir_seq, hairpin_seq]
                if line[1] in hairpin_info:
                    continue
                hairpin_info[line[1]] = [hairpin_seq, hairpin_len]
        return (mature_miRNA, hairpin_info)
