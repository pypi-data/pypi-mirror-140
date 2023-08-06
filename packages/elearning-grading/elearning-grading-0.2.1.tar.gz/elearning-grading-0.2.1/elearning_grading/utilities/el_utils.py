import os
import re
import shutil
import tarfile
import zipfile
from collections import defaultdict

import rarfile

netid_regex = r"[a-z]{3}\d{6}"
netid_find_regex = r"[A-Za-z]{3}\d{6}"
netid_find_pattern = re.compile(netid_find_regex)


def get_net_ids(text):
    netids = set()
    ordered_ids = []
    for netid in netid_find_pattern.findall(text):
        netid = netid.lower()
        if netid in netids:
            continue
        ordered_ids.append(netid)
        netids.add(netid)
    return ordered_ids


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def move(old_path, new_path, path_map):
    path_map[new_path].append(old_path)
    if os.path.exists(new_path):
        print(f"WARNING: FILE EXISTS AT {old_path} -> {new_path} ({path_map[new_path]})")
        # os.remove(new_path)
    else:
        os.rename(old_path, new_path)


def group_by_prefix(file_names, prefix_pattern):
    prefixes = defaultdict(list)
    for file_name in file_names:
        m = re.search(prefix_pattern, file_name)
        if m:
            prefix = m.group(0)
            prefixes[prefix].append(file_name)
    return prefixes


def organize_groups(file_groups, output_path, pdf_path):
    stats = defaultdict(list)
    path_map = defaultdict(list)

    for net_id, prefix_file_names in file_groups.items():
        student_path = os.path.join(output_path, net_id)
        student_pdf_path = os.path.join(pdf_path, net_id)
        # student_pdf_path = os.path.join(pdf_path, net_id + '.pdf')
        mkdir(student_pdf_path)
        mkdir(student_path)
        prefix = min([f for f in prefix_file_names if f.endswith(".txt")], key=lambda x: len(x))
        prefix_length = len(prefix) - len(".txt")
        for file_name in prefix_file_names:
            # skip text file with status stuff
            if len(file_name) == prefix_length:
                continue
            # first occurrence of netid
            new_file_name = file_name[prefix_length:]
            if new_file_name.startswith("_"):
                new_file_name = new_file_name[1:]
            old_path = os.path.join(output_path, file_name)
            new_path = os.path.join(student_path, new_file_name)
            move(old_path, new_path, path_map)
            if new_path.endswith(".zip"):
                with zipfile.ZipFile(new_path, "r") as zip_ref:
                    zip_ref.extractall(student_path)
                os.remove(new_path)
            elif new_path.endswith(".tar") or new_path.endswith(".tar.gz"):
                with tarfile.open(new_path, "r") as tar_ref:
                    tar_ref.extractall(student_path)
                os.remove(new_path)
            elif new_path.endswith(".rar"):
                try:
                    with rarfile.RarFile(new_path, "r") as rar_ref:
                        rar_ref.extractall(student_path)
                    os.remove(new_path)
                except IOError:
                    print(f"Unable to unrar rar file: {new_path}")
            elif new_file_name == ".txt":
                os.remove(new_path)

            flattened = False
            for f_name in os.listdir(student_path):
                # if our root level has the assignment pdf then we have a flattened structure
                if f_name.endswith(".pdf"):
                    flattened = True
            for f_name in os.listdir(student_path):
                dir_path = os.path.join(student_path, f_name)
                if os.path.isdir(dir_path):
                    if f_name == "__MACOSX" or f_name == ".DS_Store":
                        shutil.rmtree(dir_path)
                        continue
                    if flattened:
                        continue
                    # for d_f_name in os.listdir(dir_path):
                    # 	d_f_path = os.path.join(dir_path, d_f_name)
                    # 	new_d_f_path = os.path.join(student_path, d_f_name)
                    # 	if d_f_name == '.ipynb_checkpoints' or d_f_name == '.git':
                    # 		shutil.rmtree(d_f_path)
                    # 	else:
                    # 		move(d_f_path, new_d_f_path)
                    # shutil.rmtree(dir_path)
            seen_pdfs = []
            for f_name in os.listdir(student_path):
                f_path = os.path.join(student_path, f_name)
                if f_name.endswith(".pdf") or f_name.endswith(".docx"):
                    f_pdf_path = os.path.join(student_pdf_path, f_name)
                    move(f_path, f_pdf_path, path_map)
                    seen_pdfs.append(f_path)
            if len(seen_pdfs) > 1:
                print(seen_pdfs)
            stats[net_id].append(new_file_name)
        if len(os.listdir(student_path)) == 0:
            os.rmdir(student_path)
    return stats
