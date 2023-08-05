import argparse
import datetime
import os
import random
import tempfile
import zipfile
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Union

import exrex
from utils import netid_regex


def random_date(start: datetime.datetime, end: datetime.datetime) -> datetime.datetime:
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


def generate_random_netid() -> str:
    # [A-Za-z]{3}\d{6}
    r_netid = exrex.getone(netid_regex)
    return r_netid


def generate_random_timestamp() -> str:
    r_date = random_date(start=datetime.datetime.now() - datetime.timedelta(days=6), end=datetime.datetime.now())
    r_ts = r_date.strftime("%Y-%m-%d-%H-%M-%S")
    return r_ts


def generate_random_assignment() -> str:
    r_netid = exrex.getone(r"(Homework|Quiz|Test) [1-9]")
    return r_netid


def elearning_file_prefix(assignment: str, netid: str, timestamp: str) -> str:
    return f"{assignment}_{netid}_attempt_{timestamp}"


def generate_random_zip(assignment: str) -> str:
    assignment = assignment.replace(" ", "20")

    # gradebook_\d{4}-{uni}-{dep}-{classid}-SEC{secid}-\d{5}_{assignment.replace(' ', '20')_.zip}
    # 'gradebook_2222-UTDAL-CS-6322-SEC001-24939_Prerequisite20Form_2022-02-23-15-43-57.zip'
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    g_id = exrex.getone(r"\d{4}")
    uni_id = exrex.getone(r"[A-Z]{5}")
    dep_id = exrex.getone(r"[A-Z]{2}")
    class_id = exrex.getone(r"[3-6]\d{3}")
    sec_id = exrex.getone(r"00\d{1}")
    return f"gradebook_{g_id}-{uni_id}-{dep_id}-{class_id}-SEC{sec_id}_{assignment}_{timestamp}.zip"


class SubmissionFile(ABC):
    netid: str
    assignment: str
    timestamp: str

    def __init__(self, netid: str, assignment: str, timestamp: str):
        self.netid = netid
        self.assignment = assignment
        self.timestamp = timestamp

    def create(self, tmp: Union[str, tempfile.TemporaryDirectory]) -> str:
        file_name = elearning_file_prefix(self.assignment, self.netid, self.timestamp) + self.suffix()

        file_path = os.path.join(tmp, file_name)
        with open(file_path, "w") as f:
            f.write(self.content())
        return file_path

    @abstractmethod
    def suffix(self) -> str:
        pass

    @abstractmethod
    def content(self) -> str:
        pass


class TextSubmissionFile(SubmissionFile):
    def __init__(self, netid: str, assignment: str, timestamp: str):
        super().__init__(netid, assignment, timestamp)

    def suffix(self) -> str:
        return ".txt"

    def content(self) -> str:
        # TODO more content
        return "\n"


class PdfSubmissionFile(SubmissionFile):
    def __init__(self, netid: str, assignment: str, timestamp: str):
        super().__init__(netid, assignment, timestamp)

    def suffix(self) -> str:
        # TODO random user filenames here
        return f"_{self.assignment}.pdf"

    def content(self) -> str:
        # TODO more content
        return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_path", help="filepath to create test .zip file from eLearning.")
    parser.add_argument("-n", "--num_students", default=40, type=int, help="Number of students to put in file.")
    parser.add_argument("-s", "--seed", default=0, type=int, help="Seed of RNG.")
    parser.add_argument(
        "-t",
        "--type",
        default="pdf",
        help="Type of data to generate. Options: "
        "pdf: only generates pdf files. "
        "pdf-zip: only generates pdf files inside zip files."
        "pdf-code-zip: generates pdf file and code files inside zip files."
        "pdf-code-full: generates pdf file and code files inside various compressed files.",
    )
    args = parser.parse_args()
    # gen_type = args.type
    output_path = args.output_path
    num_students = args.num_students
    random.seed(args.seed)

    net_ids = set()
    while len(net_ids) < num_students:
        r_netid = generate_random_netid()
        net_ids.add(r_netid)
    net_ids = list(net_ids)
    random.shuffle(net_ids)

    assignment = generate_random_assignment()
    file_types = [TextSubmissionFile, PdfSubmissionFile]
    output_name = generate_random_zip(assignment)
    output_filepath = os.path.join(output_path, output_name)

    with tempfile.TemporaryDirectory() as tmp:
        files = []
        for netid in net_ids:
            timestamp = generate_random_timestamp()
            for sub_file_type in file_types:
                sub_file = sub_file_type(netid, assignment, timestamp)
                sub_file_path = sub_file.create(tmp)
                files.append(sub_file_path)
        # gradebook_2222-UTDAL-CS-6322-SEC001-24939_Prerequisite20Form_2022-02-23-15-43-57
        with zipfile.ZipFile(output_filepath, "w") as zf:
            for file_path in files:
                zf.write(file_path, os.path.basename(file_path))


if __name__ == "__main__":
    main()
