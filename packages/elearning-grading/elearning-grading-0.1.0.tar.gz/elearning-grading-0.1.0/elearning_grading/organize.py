import argparse
import os
import zipfile

import utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", help="filepath to .zip file from eLearning.")
    parser.add_argument("-c", "--code_path", default="code", help="output folder for code, organized by netid.")
    parser.add_argument(
        "-r", "--reports_path", default="reports", help="output folder for pdf reports, organized by netid."
    )

    args = parser.parse_args()

    input_path = args.input_path
    code_path = args.code_path
    reports_path = args.reports_path

    utils.mkdir(code_path)
    utils.mkdir(reports_path)

    with zipfile.ZipFile(input_path, "r") as zip_ref:
        zip_ref.extractall(code_path)

    file_names = os.listdir(code_path)
    file_groups = utils.group_by_prefix(file_names, utils.netid_lower_regex)

    stats = utils.organize_groups(file_groups, code_path, reports_path)

    # for net_id, files in stats.items():
    # 	print(f'{net_id}: nrof_files={len(files)}')

    print("----------------")
    print(f"Number of Students: {len(stats)}")


if __name__ == "__main__":
    main()
