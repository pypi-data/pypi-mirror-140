import argparse
import datetime
import functools
import os
import random
import shutil
import tempfile
import zipfile
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import timedelta
from typing import Dict, List, Optional, Set, Type, Union

import exrex

from elearning_grading.utilities import netid_regex


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
    name: str
    file_names = List[str]
    file_types = List[str]

    def __init__(self, netid: str, assignment: str, timestamp: str):
        self.netid = netid
        self.assignment = assignment
        self.timestamp = timestamp
        self.file_names = [elearning_file_prefix(self.assignment, self.netid, self.timestamp)]
        self.file_types = []

    def create(self, tmp: Union[str, tempfile.TemporaryDirectory]) -> str:
        file_name = self.filename()
        file_path = os.path.join(tmp, file_name)
        with open(file_path, "w") as f:
            f.write(self.content())
        return file_path

    def filename(self) -> str:
        return random.choice(self.file_names) + random.choice(self.file_types)

    @abstractmethod
    def content(self) -> str:
        pass


class TextSubmissionFile(SubmissionFile):
    def __init__(self, netid: str, assignment: str, timestamp: str):
        super().__init__(netid, assignment, timestamp)
        self.file_types = [".txt"]

    def content(self) -> str:
        # TODO more content
        return "\n"


class PdfSubmissionFile(SubmissionFile):
    def __init__(self, netid: str, assignment: str, timestamp: str):
        super().__init__(netid, assignment, timestamp)
        self.file_names = [
            # TODO random user assignment file names
            elearning_file_prefix(self.assignment, self.netid, self.timestamp)
            + f"_{self.assignment}"
        ]
        self.file_types = [".pdf"]

    def content(self) -> str:
        # TODO more content
        return ""


class ZipSubmissionFile(SubmissionFile):
    archive_types: List[Type[SubmissionFile]]

    def __init__(self, archive_types: List[Type[SubmissionFile]], netid: str, assignment: str, timestamp: str):
        super().__init__(netid, assignment, timestamp)
        self.archive_types = archive_types
        self.file_names = [
            # TODO random user assignment file names
            elearning_file_prefix(self.assignment, self.netid, self.timestamp)
            + f"_{self.assignment}"
        ]
        self.file_types = [".zip"]

    @staticmethod
    def add_folder(root_path: str, zf: zipfile.ZipFile, seen_filenames: Set[str]):
        root_base = os.path.basename(root_path)
        for root, folders, files in os.walk(root_path):
            for item in folders + files:
                item_path = os.path.join(root, item)
                rel_base = os.path.relpath(item_path, root_path)
                rel_path = os.path.join(root_base, rel_base)
                if rel_path not in seen_filenames:
                    zf.write(item_path, rel_path)
                    seen_filenames.add(rel_path)

    def create(self, tmp: Union[str, tempfile.TemporaryDirectory]) -> str:
        file_name = self.filename()
        file_path = os.path.join(tmp, file_name)

        with zipfile.ZipFile(file_path, "w") as zf, tempfile.TemporaryDirectory() as zf_tmp:
            seen_filenames = set()
            for a_type in self.archive_types:
                file = a_type(self.netid, self.assignment, self.timestamp)
                tmp_file_path = file.create(zf_tmp)
                tmp_file_name = os.path.basename(tmp_file_path)
                if tmp_file_name not in seen_filenames:
                    zf.write(tmp_file_path, tmp_file_name)
                    seen_filenames.add(tmp_file_name)
                if os.path.isdir(tmp_file_path):
                    self.add_folder(tmp_file_path, zf, seen_filenames)
                    shutil.rmtree(tmp_file_path)
                else:
                    os.remove(tmp_file_path)

        return file_path

    def content(self) -> str:
        return ""


class PdfStudentFile(SubmissionFile):
    def __init__(self, netid: str, assignment: str, timestamp: str):
        super().__init__(netid, assignment, timestamp)
        self.file_names = ["report", "hw", self.assignment, self.netid, exrex.getone(r"[a-zA-Z]{6}")]
        self.file_types = [".pdf"]

    def content(self) -> str:
        # TODO random content
        return ""


class TextStudentFile(SubmissionFile):
    def __init__(self, netid: str, assignment: str, timestamp: str):
        super().__init__(netid, assignment, timestamp)
        self.file_names = [exrex.getone(r"([a-zA-Z]{6})")]
        self.file_types = [".txt", ".md", ".MD", ".TXT", ""]

    def content(self) -> str:
        # TODO random content
        return ""


class ReadmeStudentFile(SubmissionFile):
    def __init__(self, netid: str, assignment: str, timestamp: str):
        super().__init__(netid, assignment, timestamp)
        # TODO more random readme names
        self.file_names = ["readme", "README", "ReadMe", self.netid]
        self.file_types = [".txt", ".md", ".TXT", ".MD", ".pdf", ""]

    def content(self) -> str:
        # TODO random content
        return ""


class CodeStudentFile(SubmissionFile):
    def __init__(self, netid: str, assignment: str, timestamp: str):
        super().__init__(netid, assignment, timestamp)
        self.file_names = [exrex.getone(r"(p|problem|answer|hw)\d")]
        self.file_types = [".py", ".java"]

    def content(self) -> str:
        # TODO random code content
        return ""


class ZipStudentFile(ZipSubmissionFile):
    def __init__(self, archive_types: List[Type[SubmissionFile]], netid: str, assignment: str, timestamp: str):
        super().__init__(archive_types, netid, assignment, timestamp)
        self.file_names = ["code", "hw", "assignment", exrex.getone(r"([a-zA-Z]{6})")]
        # TODO enable tar, tar.gz, and rar archives
        self.file_types = [".zip"]


class FolderStudentFile(ZipStudentFile):
    def __init__(self, archive_types: List[Type[SubmissionFile]], netid: str, assignment: str, timestamp: str):
        super().__init__(archive_types, netid, assignment, timestamp)
        self.file_names = ["code", "hw", "assignment", exrex.getone(r"([a-zA-Z]{6})")]
        self.file_types = [""]

    def create(self, tmp: Union[str, tempfile.TemporaryDirectory]) -> str:
        file_name = self.filename()
        file_path = os.path.join(tmp, file_name)
        os.mkdir(file_path)
        for a_type in self.archive_types:
            file = a_type(self.netid, self.assignment, self.timestamp)
            file.create(file_path)
        return file_path


class RandomZipSubmissionFileBuilder:
    max_depth: int
    min_files: int
    max_files: int

    def __init__(self, min_files: int = 0, max_files: int = 6, max_depth: int = 2):
        super().__init__()
        self.min_files = min_files
        self.max_files = max_files
        self.max_depth = max_depth
        # TODO make this more random
        self.required_types = {PdfStudentFile: 1, ReadmeStudentFile: 1, TextStudentFile: 1, CodeStudentFile: 1}
        # TODO track counts of each type for deterministic file naming with numbering
        self.random_options = {
            PdfStudentFile: 1,
            ReadmeStudentFile: None,
            TextStudentFile: None,
            CodeStudentFile: None,
            ZipStudentFile: None,
            FolderStudentFile: None,
        }

    def __call__(self, netid: str, assignment: str, timestamp: str) -> ZipSubmissionFile:
        # student_structure = [
        #     PdfStudentFile,
        #     ReadmeStudentFile,
        #     TextStudentFile,
        #     CodeStudentFile
        # ]
        options = self.random_options.copy()
        seen = defaultdict(int)
        student_structure = self.build(netid, assignment, timestamp, seen_types=seen, options=options)
        return ZipSubmissionFile(student_structure, netid, assignment, timestamp)

    def build(
        self,
        netid: str,
        assignment: str,
        timestamp: str,
        seen_types: Dict[Type[SubmissionFile], int],
        options: Dict[Type[SubmissionFile], Optional[int]],
        depth: int = 0,
    ) -> List[Type[SubmissionFile]]:
        structure = []
        # inclusive
        num_depth_files = random.randint(self.min_files, self.max_files)

        for _ in range(num_depth_files):
            r_type = random.choice(
                [
                    f_type
                    for f_type, f_count in options.items()
                    # ignore types which
                    # (a) have a f_count <= 0, or
                    # (b) ZipStudentFile / FolderStudentFile and depth == max_depth
                    if (f_count is None or seen_types[f_type] < f_count)
                    and (not issubclass(f_type, ZipStudentFile) or depth != self.max_depth)
                ]
            )
            seen_types[r_type] += 1
            if issubclass(r_type, ZipStudentFile):
                r_type = functools.partial(
                    r_type, self.build(netid, assignment, timestamp, seen_types, options, depth + 1)
                )
            structure.append(r_type)

        # if we have not generated all the needed files in sub-folders / archives,
        # then add required files to root
        if depth == 0:
            for r_type, r_min in self.required_types.items():
                if seen_types[r_type] < r_min:
                    structure.append(r_type)
                    seen_types[r_type] += 1

        return structure


gen_configs = {
    "pdf": [TextSubmissionFile, PdfSubmissionFile],
    "pdf-zip": [TextSubmissionFile, functools.partial(ZipSubmissionFile, [PdfStudentFile])],
    "pdf-code-zip": [
        TextSubmissionFile,
        functools.partial(ZipSubmissionFile, [PdfStudentFile, ReadmeStudentFile, TextStudentFile, CodeStudentFile]),
    ],
    # TODO student-level consistency
    "pdf-code-full": [TextSubmissionFile, RandomZipSubmissionFileBuilder(max_depth=2, max_files=6)],
}


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
    gen_type = args.type
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
    file_types = gen_configs[gen_type]
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
        with zipfile.ZipFile(output_filepath, "w") as zf:
            for file_path in files:
                zf.write(file_path, os.path.basename(file_path))


if __name__ == "__main__":
    main()
