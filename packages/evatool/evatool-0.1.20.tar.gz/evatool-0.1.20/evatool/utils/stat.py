#!/usr/bin/env python
# -*- conding:utf-8 -*-
# @AUTHOR: Gui-Yan Xie
# @CONTACT: xieguiyan at hust dot edu dot cn
# @DATE: 2021-09-27 17:04:16
# @DESCRIPTION:

from .tag import Tag
from .fastq import Fastq
import re
import sys
import copy
from collections import Counter


class Stat(object):
    def __init__(self, fastq: Fastq, tag: Tag):
        self.fastq = fastq
        self.tag = tag
        self.tag_fa = f"{self.fastq.outputdir}/{self.fastq.inputfile.stem}.fa"
        self.samprefix = f"{self.fastq.outputdir}/{self.fastq.inputfile.stem}"
        self.function_ncRNA_lst = ["miRNA", "piRNA", "snoRNA", "snRNA", "YRNA"]

    def get_true_miRexp(self, tag_ref_dict, hairpin_tag_dict):
        # divide_tag_expressoin_dict = {}
        mir_exp_dict = {}
        # tag_with_multi_assign_dict = {tag: ref for tag, ref in tag_hairpin_dict.items() if len(ref) > 1}
        # sorted_tagn_4_multi_maps = sorted(tag_with_multi_assign_dict.keys(), key=lambda a: self.tag.tag_count_dict[a], reverse=True)
        for tag in tag_ref_dict:
            # hairpins_n = len(hairpins)
            tag_count = self.tag.tag_count_dict[tag]
            refs_mir = set()
            # tmp_dict = {}
            refs = list(tag_ref_dict[tag].keys())
            for ref in refs:
                mapped_details = tag_ref_dict[tag][ref]
                for mapped_detail in mapped_details:
                    arm = mapped_detail[-1]
                    if arm in self.fastq.config.mature_miRNA[ref]:
                        mir = self.fastq.config.mature_miRNA[ref][arm][0]
                    else:
                        arm = str(8 - int(arm[0])) + "p"
                        mir = ref + "-" + arm
                    refs_mir.add(mir)
                    # tmp_dict.setdefault(mir, set()).add(hairpin)
            mir_n = len(refs_mir)
            if mir_n == 1:
                tag_count_division = tag_count
            else:
                tag_count_division = int(tag_count / mir_n) + 1
            for j in refs_mir:
                if j in mir_exp_dict:
                    mir_exp_dict[j] += tag_count_division
                else:
                    mir_exp_dict[j] = tag_count
        return mir_exp_dict

    def get_mirna_editing(self, split2):
        re_edit = re.compile(r"MD:Z:(\d+)(.*)(G+)\s+")
        m = re_edit.search(split2)
        if m:
            return True
        else:
            return False

    def get_edit_distance(self, split2):
        re_edit = re.compile(r"NM:i:(\d)")
        m = re_edit.search(split2)
        mirna_edit = self.get_mirna_editing(split2)
        if m:
            if mirna_edit == True and int(m.group(1)) == 2:
                mapped_distance = 1
            else:
                mapped_distance = int(m.group(1))
        else:
            mapped_distance = 0
        return mapped_distance

    def get_mismatch(self, split2, mapped_start):
        re_mis = re.compile(r"MD:Z:(\d+)[A-Z]?(\d*)")
        mis_str = re_mis.search(split2)
        mismatch_loci = int(mis_str.group(1)) + int(mapped_start) - 1
        return mismatch_loci

    def get_discard_flag(self, split2, mapped_start, mapped_ref):
        discard_flag = 0
        mismatch_loci = self.get_mismatch(split2=split2, mapped_start=mapped_start)
        mir_seed_regions = [(z[1] + 1, z[1] + 7) for z in self.fastq.config.mature_miRNA[mapped_ref].values()]
        for region in mir_seed_regions:
            if region[0] <= mismatch_loci <= region[1]:
                discard_flag = 1
        return discard_flag

    def load_nc_samfile(self):
        mapped_nc_tag_dict = {}
        tag_ref_detail = {}
        ref_tag_detail = {}
        for n, i in enumerate(self.fastq.ncrna_lst):
            tag_ref_detail[i] = {}
            ref_tag_detail[i] = {}
            with open(f"{self.samprefix}.{i}.sam", "r") as sf:
                for j in sf:
                    line = j.strip().split("\t")
                    split1, split2 = re.split(pattern="\t*IIII*\t", string=j)
                    tag_name, flag, mapped_ref, mapped_start = [split1.split(sep="\t")[i] for i in [0, 1, 2, 3]]
                    if flag != "0":
                        continue
                    mapped_distance = self.get_edit_distance(split2)
                    if tag_name.startswith("@") or mapped_distance > 1:
                        continue
                    if n:
                        if tag_name in mapped_nc_tag_dict:
                            continue
                        tag_ref_detail[i].setdefault(tag_name, set()).add(mapped_ref)
                    else:
                        arm = "3p"
                        if self.fastq.config.hairpin_info[line[2]][-1] - int(line[3]) * 2 - len(line[9]) + 1 > 0:
                            arm = "5p"
                        if mapped_distance:
                            discard_flag = self.get_discard_flag(split2, mapped_start, mapped_ref)
                            if discard_flag:
                                continue
                        try:
                            tag_ref_detail[i].setdefault(tag_name, {})[mapped_ref].append([mapped_start, mapped_distance, arm])
                        except KeyError:
                            tag_ref_detail[i].setdefault(tag_name, {})[mapped_ref] = [[mapped_start, mapped_distance, arm]]
                    ref_tag_detail[i].setdefault(mapped_ref, set()).add(tag_name)
                    mapped_nc_tag_dict[tag_name] = i
        return tag_ref_detail, ref_tag_detail, mapped_nc_tag_dict

    def get_ncRNAs_exp(self):
        ref_exp = {}
        mapped_ncRNA_counts = {}
        (tag_ref_detail, ref_tag_detail, mapped_nc_tag_dict) = self.load_nc_samfile()
        for n, i in enumerate(self.fastq.ncrna_lst):
            ref_exp[i] = {}
            mapped_tags = tag_ref_detail[i].keys()
            mapped_ncRNA_counts[i] = sum([self.tag.tag_count_dict[tag] for tag in mapped_tags])
            if n:
                for ref in ref_tag_detail[i]:
                    ref_counts = sum([self.tag.tag_count_dict[xx] for xx in ref_tag_detail[i][ref]])
                    ref_exp[i][ref] = ref_counts
            else:
                mir_exp_dict = self.get_true_miRexp(tag_ref_detail[i], ref_tag_detail[i])
                ref_exp[i] = mir_exp_dict
        return (ref_exp, mapped_ncRNA_counts, mapped_nc_tag_dict, ref_tag_detail)

    def sub_dict_modify(self, dct, keys, flag):
        if flag == 1:
            return dict([(key, dct.get(key)) for key in keys])
        else:
            return dict([(key, dct.get(key)) for key in dct.keys() - keys])

    def deal_mapped_unanno_info(self, mapped_nc_tag_dict, ref_exp, un_annotated_tags):
        map_to_genome_tags = set()
        tmp_anno = []
        rebuilt_unanno_info = []
        with open(f"{self.samprefix}.genome.unanno.info", "r") as uf:
            for i in uf:
                line = i.strip().split("\t")
                tags_id = line[4].strip().split(",")
                map_to_genome_tags.update(tags_id)
                tags_in_nc = [tag_id for tag_id in tags_id if tag_id in mapped_nc_tag_dict]
                # tag_type_lst = [mapped_nc_tag_dict[tag] for tag in tags_in_nc]
                if tags_in_nc:
                    tag_type_lst = [mapped_nc_tag_dict[tag] for tag in tags_in_nc]
                    tag_type_counter = Counter(tag_type_lst)
                    sorted_tag_type_counter = sorted(tag_type_counter.keys(), key=lambda a: tag_type_counter[a], reverse=True)
                    tag_type = sorted_tag_type_counter[0]
                    if "other" in ref_exp[tag_type]:
                        ref_exp[tag_type]["other"] += sum([self.tag.tag_count_dict[t_z] for t_z in tags_id if t_z not in mapped_nc_tag_dict])
                    else:
                        ref_exp[tag_type]["other"] = sum([self.tag.tag_count_dict[t_z] for t_z in tags_id if t_z not in mapped_nc_tag_dict])
                    tmp_anno.extend(tags_id)
                    for t_z in tags_id:
                        mapped_nc_tag_dict[t_z] = tag_type
                else:
                    rebuilt_unanno_info.append(i)
            un_annotated_tags = self.sub_dict_modify(un_annotated_tags, set(tmp_anno), 2)
        return map_to_genome_tags, un_annotated_tags, mapped_nc_tag_dict, ref_exp, rebuilt_unanno_info

    def deal_mapped_anno_info(self, un_annotated_tags, map_to_genome_tags, mapped_nc_tag_dict, ref_exp):
        mapped_anno_bed = f"{self.samprefix}.genome.annotation.info"
        details_mapped_tag = {}
        with open(mapped_anno_bed, "r") as mf:
            anno_c_set = []
            new_anno_tags = set()
            un_annotated_tags_tmp = un_annotated_tags.keys()
            for i in mf:
                line = i.strip().split("\t")
                ref_gene_info = line[-9:]
                mapped_info = line[0:7]
                tags_id = mapped_info[4].strip().split(",")
                map_to_genome_tags.update(tags_id)
                unanno_flag = [tag_id for tag_id in tags_id if tag_id in un_annotated_tags_tmp]
                tags_in_nc = [tag_id for tag_id in tags_id if tag_id in mapped_nc_tag_dict]
                if unanno_flag:
                    if tags_in_nc and tags_in_nc not in anno_c_set:
                        tag_type_lst = [mapped_nc_tag_dict[tag] for tag in tags_in_nc]
                        tag_type_counter = Counter(tag_type_lst)
                        sorted_tag_type_counter = sorted(tag_type_counter.keys(), key=lambda a: tag_type_counter[a], reverse=True)
                        tag_type = sorted_tag_type_counter[0]
                        if "other" in ref_exp[tag_type]:
                            ref_exp[tag_type]["other"] += sum([self.tag.tag_count_dict[t_z] for t_z in tags_id if t_z not in mapped_nc_tag_dict])
                        else:
                            ref_exp[tag_type]["other"] = sum([self.tag.tag_count_dict[t_z] for t_z in tags_id if t_z not in mapped_nc_tag_dict])
                        new_anno_tags.update(unanno_flag)
                        for t_z in tags_id:
                            mapped_nc_tag_dict[t_z] = tag_type
                        anno_c_set.append(tags_in_nc)
                strand = "genebody" if mapped_info[3] == ref_gene_info[5] else "opposite"
                try:
                    details_mapped_tag[mapped_info[4]][strand].append(ref_gene_info)
                except KeyError:
                    details_mapped_tag.setdefault(mapped_info[4], {})[strand] = [ref_gene_info]
                    details_mapped_tag[mapped_info[4]]["l"] = mapped_info
            un_annotated_tags = self.sub_dict_modify(un_annotated_tags, new_anno_tags, 2)
        return details_mapped_tag, map_to_genome_tags, un_annotated_tags, ref_exp

    def deal_mapped_info(self, mapped_nc_tag_dict, ref_exp):
        # map_to_genome_tags = set()
        new_anno_tag_detail = {}
        region_anno_detail = {}
        # rebuilt_unanno_info = []
        un_annotated_tags_nc = {tag_id: self.tag.tag_count_dict[tag_id] for tag_id in self.tag.tag_count_dict if tag_id not in mapped_nc_tag_dict}
        un_annotated_tags = copy.deepcopy(un_annotated_tags_nc)
        (map_to_genome_tags, un_annotated_tags, mapped_nc_tag_dict, ref_exp, rebuilt_unanno_info) = self.deal_mapped_unanno_info(mapped_nc_tag_dict, ref_exp, un_annotated_tags)
        (details_mapped_tag, map_to_genome_tags, un_annotated_tags, ref_exp) = self.deal_mapped_anno_info(un_annotated_tags, map_to_genome_tags, mapped_nc_tag_dict, ref_exp)
        for tags in details_mapped_tag:
            strand_lst = ["genebody", "opposite"]
            tag_anno_dict = dict([(z, "-") for z in strand_lst])
            tag_ids = tags.strip().split(",")
            detail_info = details_mapped_tag[tags]
            mapped_info = detail_info["l"]
            mapped_start = int(mapped_info[1])
            mapped_end = int(mapped_info[2])
            for strand_flag in strand_lst:
                if strand_flag not in detail_info:
                    continue
                ref_lst = detail_info[strand_flag]
                try:
                    tmp_lst = sorted(ref_lst, key=lambda a: abs(int(a[1]) - mapped_start) + abs(int(a[2]) - mapped_end), reverse=True)
                except Exception:
                    print(strand_flag)
                    print(ref_lst)
                    sys.exit()
                out_tmp_lst = [":".join([a[-1], a[3], a[6]]) for a in tmp_lst]
                tag_anno_dict[strand_flag] = out_tmp_lst
            for tag in tag_ids:
                new_anno_tag_detail[tag] = tag_anno_dict
            region_anno_detail[":".join(mapped_info)] = tag_anno_dict
        return (map_to_genome_tags, new_anno_tag_detail, region_anno_detail, rebuilt_unanno_info, ref_exp)

    def stat_each_ncRNA_exp(self, i, mapped_nc_tag_dict, mapped_ncRNA_counts, ref_exp, ref_tag_detail, total_mapped_tags_sum, exp_cal_category) -> None:
        total_mapped_nc_tags_sum = sum([self.tag.tag_count_dict[j] for j in mapped_nc_tag_dict])
        function_nc_tags_sum_ori = sum([mapped_ncRNA_counts.get(j, 0) for j in self.function_ncRNA_lst])
        exp_cal_method = {"total": total_mapped_tags_sum, "ncRNAall": total_mapped_nc_tags_sum, "func": function_nc_tags_sum_ori}
        ncRNA_exp_file = open(f"{self.samprefix}.{i}.exp", "w")
        ncRNA_exp_file.write("GeneSymbol\tTagCount\tRPM\n")
        tag_mapped_catagory_handle = open(f"{self.samprefix}.tag.ncRNA.classification", "w")
        tag_mapped_catagory_handle.write("TagId\tTagCount\tCategory\tMappedItem\tRegion\n")
        for j in ref_exp[i]:
            if j == "other":
                continue
            if j in ref_tag_detail[i]:
                tmp_mapped_tags = ref_tag_detail[i][j] if j in ref_tag_detail[i] else []
                for t in tmp_mapped_tags:
                    tmp_tag_count = self.tag.tag_count_dict[t]
                    tag_mapped_catagory_handle.write(t + "\t" + str(tmp_tag_count) + "\t" + i + "\t" + j + "\treference\n")
            nc_exp = ref_exp[i][j] / exp_cal_method[exp_cal_category] * 1000000
            ncRNA_exp_file.write("{0}\t{1:d}\t{2:.2f}\n".format(j, ref_exp[i][j], nc_exp))
        ncRNA_exp_file.close()

    def stat_ncRNA_exp(self, map_to_genome_tags, mapped_nc_tag_dict, mapped_ncRNA_counts, ref_exp, ref_tag_detail) -> None:
        total_counts = sum(self.tag.tag_count_dict.values())
        ncRNA_exp_stat = open(f"{self.samprefix}.stat", "w")
        total_mapped_tags_sum = sum([self.tag.tag_count_dict[j] for j in map_to_genome_tags])
        total_mapped_tags_ratio = total_mapped_tags_sum / total_counts * 100
        ncRNA_exp_stat.write(f"#Total counts: {total_counts}\n#Total mapped counts: {total_mapped_tags_sum}({total_mapped_tags_ratio:.2f}%)\n")
        ncRNA_exp_stat.write(f"#Unmapped tags: {total_counts - total_mapped_tags_sum}({100 - total_mapped_tags_ratio:.2f}%)\nCategory\tMappedTag\tRatio\n")
        exp_cal_category = self.fastq.config.config["RPM"]
        ncRNA_type_list = {"total": self.fastq.ncrna_lst, "func": self.function_ncRNA_lst}
        for n, i in enumerate(ncRNA_type_list[exp_cal_category]):
            self.stat_each_ncRNA_exp(i, mapped_nc_tag_dict, mapped_ncRNA_counts, ref_exp, ref_tag_detail, total_mapped_tags_sum, exp_cal_category)
            nc_counts_sum = sum([ref_exp[i][j] for j in ref_exp[i] if j != "other"])
            ncRNA_exp_stat.write("{0}\t{1:d}\t{2:.2f}%\n".format(i, nc_counts_sum, nc_counts_sum / total_mapped_tags_sum * 100))
            self.fastq.log.log(f"calcultion for expression of {i} completed")
        ncRNA_exp_stat.close()

    def tag_genome_classfication(self, new_anno_tag_detail):
        tag_mapped_genome_catagory_handle = open(f"{self.samprefix}.tag.genome.classification", "w")
        tag_mapped_genome_catagory_handle.write("TagId\tTagCount\tGenebody\tOpposite\n")
        for tag in new_anno_tag_detail:
            tag_count = self.tag.tag_count_dict[tag]
            tag_anno_info = new_anno_tag_detail[tag]
            tag_mapped_genome_catagory_handle.write(tag + "\t" + str(tag_count))
            for strand in ["genebody", "opposite"]:
                if strand in tag_anno_info:
                    out_mapped_items = ";".join(tag_anno_info[strand])
                else:
                    out_mapped_items = "-"
                tag_mapped_genome_catagory_handle.write("\t" + out_mapped_items)
            tag_mapped_genome_catagory_handle.write("\n")
        self.fastq.log.log("ncRNA expression analysis completed")

    def region_anno_genome_classification(self, region_anno_detail):
        region_mapped_genome_catagory_handle = open(f"{self.samprefix}.region.anno.genome.classification", "w")
        region_mapped_genome_catagory_handle.write("GenomeRegion\tGeneBody\tOpposite\n")
        for region in region_anno_detail:
            region_anno = region_anno_detail[region]
            region_mapped_genome_catagory_handle.write(region)
            for strand in ["genebody", "opposite"]:
                region_mamped_info = ";".join(region_anno[strand]) if strand in region_anno else "-"
                region_mapped_genome_catagory_handle.write("\t" + region_mamped_info)
            region_mapped_genome_catagory_handle.write("\n")

    def tag_unmapped(self, map_to_genome_tags):
        un_mapped_tag = set(self.tag.tag_count_dict.keys()) - map_to_genome_tags
        tag_unmapped_handle = open(f"{self.samprefix}.tag.unmapped", "w")
        with open(f"{self.samprefix}.fa", "r") as tmp_f:
            out_flag = 0
            for tmp_line in tmp_f:
                if tmp_line.startswith(">"):
                    tag_line = tmp_line.strip(">\n").split("\t")
                    if tag_line[0] in un_mapped_tag:
                        tag_unmapped_handle.write(tmp_line)
                        out_flag = 1
                elif out_flag:
                    tag_unmapped_handle.write(tmp_line)
                    out_flag = 0
        self.fastq.log.log("Genome annotation completed!")

    def stat_match(self):
        (ref_exp, mapped_ncRNA_counts, mapped_nc_tag_dict, ref_tag_detail) = self.get_ncRNAs_exp()
        (map_to_genome_tags, new_anno_tag_detail, region_anno_detail, rebuilt_unanno_info, ref_exp) = self.deal_mapped_info(mapped_nc_tag_dict, ref_exp)
        self.stat_ncRNA_exp(map_to_genome_tags, mapped_nc_tag_dict, mapped_ncRNA_counts, ref_exp, ref_tag_detail)
        self.tag_genome_classfication(new_anno_tag_detail)
        self.region_anno_genome_classification(region_anno_detail)
        region_unanno_file_handle = open(f"{self.samprefix}.region.unanno.genome.classification", "w")
        region_unanno_file_handle.write("Chromosome\tStart\tEnd\tStrand\tTags\tTotalCount\tMean\n")
        for chr_region in rebuilt_unanno_info:
            region_unanno_file_handle.write(chr_region)
        self.tag_unmapped(map_to_genome_tags)
