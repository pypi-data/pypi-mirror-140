import argparse
import os
import shutil
from collections import defaultdict

import pandas as pd

from elearning_grading.utilities.el_utils import get_net_ids


def collect_team_files(team_map, root_dir):
    team_files = defaultdict(list)
    for file in os.listdir(root_dir):
        file_path = os.path.join(root_dir, file)
        if file.endswith(".pdf") or file.endswith(".docx") or file.endswith(".zip"):
            netids = get_net_ids(file)
            if len(netids) == 1:
                netid = netids[0]
                team_id = team_map[netid]
                team_files[team_id].append(file_path)
            elif len(netids) > 1:
                print(f"ERROR: File {file} has multiple netids: {netids}")
            else:
                print(f"ERROR: File {file} has no netids!")
        else:
            continue
    return team_files


def load_teams(team_file):
    df = pd.read_excel(team_file)
    df = df[["Username", "Team"]].set_index("Username")
    df = df.to_dict()["Team"]
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", help="filepath to folder of student project files.")
    parser.add_argument(
        "-t", "--team_path", help="filepath to excel file containing team membership. " "Format: netid, team_id"
    )
    parser.add_argument("-o", "--output_path", help="filepath to output grouped student files by team membership.")

    args = parser.parse_args()
    out_dir = args.output_path

    team_map = load_teams(args.team_path)
    team_files = collect_team_files(team_map, args.input_path)

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    for team_id, t_files in team_files.items():
        for f_idx, file_path in enumerate(t_files):
            f_name = f"team-{team_id}"
            if f_idx != 0:
                f_name = f"{f_name}-{f_idx}"
            file_type = os.path.splitext(file_path)[-1]
            f_name = f"{f_name}{file_type}"
            new_file_path = os.path.join(out_dir, f_name)
            # print(f'{team_id}-{f_idx} ({file_path} -> {new_file_path}')
            shutil.copy(file_path, new_file_path)


if __name__ == "__main__":
    main()
