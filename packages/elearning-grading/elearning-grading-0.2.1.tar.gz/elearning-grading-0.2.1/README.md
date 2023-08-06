<div align="center">

# eLearning Grading

**Python utilities to help Teaching Assistants grade assignments with eLearning**


______________________________________________________________________


[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/elearning-grading)](https://pypi.org/project/elearning-grading/)
[![PyPI Status](https://badge.fury.io/py/elearning-grading.svg)](https://badge.fury.io/py/elearning-grading)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/Supermaxman/elearning-grading/blob/master/LICENSE.txt)

</div>

______________________________________________________________________

## eLearning Grading

This repository contains python scripts and tools to help Teaching Assistants
using eLearning's assignment download feature to organize and grade written, typed, and programming assignments.

## How To Use
### Installing from pip
```bash
pip install elearning-grading
```

### Installing from GitHub
```bash
git clone https://github.com/Supermaxman/elearning-grading
cd elearning-grading
pip install -e .
```

### Organizing code and reports
eLearning provides the `Assignment File Download` feature for Teaching Assistants to download assignment files 
for the entire class. 
Sadly, this feature makes grading assignments extremely tedious, 
as the .zip file provided usually looks like this (simulated):
<div align="left">
    <img src="docs/images/ex1.PNG?raw=true" width="400px">
</div>

With each student submission zip file populated with user-submitted content:
<div align="left">
    <img src="docs/images/ex2.PNG?raw=true" width="400px">
</div>

These archives could be .zip, .tar, .tar.gz, .rar, or more file types, and there could
be multiple files for each student in the eLearning zip file.
`elearning-grading` helps manage this chaos by organizing files and folders
based on student netids, and splitting code and pdf reports.

The `elg-org` tool works as follows:

```bash
elg-org --help
usage: elg-org [-h] [-i INPUT_PATH] [-c CODE_PATH] [-r REPORTS_PATH]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_PATH, --input_path INPUT_PATH
                        filepath to .zip file from eLearning.
  -c CODE_PATH, --code_path CODE_PATH
                        output folder for code, organized by netid.
  -r REPORTS_PATH, --reports_path REPORTS_PATH
                        output folder for pdf reports, organized by netid.
```

For example, the above simulated eLearning submission zip file is organized like so:

```bash
elg-org -i tests/gradebook_7366-LRWYV-CO-3865-SEC000_Test207_2022-02-24-11-32-57.zip
```
PDF or DOCX reports are organized into the `reports` folder, while 
everything else is considered potential `code` and is moved into the 
`code` folder.
<div align="left">
    <img src="docs/images/ex3.PNG?raw=true" width="300px">
</div>

Each folder is organized by student netid as follows:
<div align="left">
    <img src="docs/images/ex4.PNG?raw=true" width="300px">
</div>

Where reports are included in `reports` folder for each netid:
<div align="left">
    <img src="docs/images/ex5.PNG?raw=true" width="300px">
</div>

And code is included in the `code` folder for each netid:
<div align="left">
    <img src="docs/images/ex6.PNG?raw=true" width="300px">
</div>

This organization structure makes grading much easier, as everything 
is organized by netid and written reports are clearly marked for 
grading.


### Generating simulated eLearning .zip files
eLearning's `Assignment File Download` feature provides extremely unpredictable 
student zip files, as each student can upload whatever they want. 
`elearning-grading` provides the `elg-gen` utility, which generates 
synthetic, random files in the unpredictable format of eLearning.
`elg-gen` ensures that utilities within this library are 
tested against unexpected student file formats.

`el-gen` documentation:
```bash
elg-gen --help
usage: elg-gen [-h] [-o OUTPUT_PATH] [-n NUM_STUDENTS] [-s SEED] [-t TYPE]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        filepath to create test .zip file from eLearning.
  -n NUM_STUDENTS, --num_students NUM_STUDENTS
                        Number of students to put in file.
  -s SEED, --seed SEED  Seed of RNG.
  -t TYPE, --type TYPE  Type of data to generate. Options: pdf: only generates
                        pdf files. pdf-zip: only generates pdf files inside zip
                        files.pdf-code-zip: generates pdf file and code files
                        inside zip files.pdf-code-full: generates pdf file and
                        code files inside various compressed files.
```
`el-gen` usage:
```bash
elg-gen -n 5 \
  --output_path tests \
  --type pdf-code-full \
  --seed 1
```

This will generate an eLearning `Assignment File Download` file format filled with 
random data, such as the following:
`gradebook_7366-LRWYV-CO-3865-SEC000_Test207_2022-02-24-11-32-57.zip`
<div align="left">
    <img src="docs/images/ex1.PNG?raw=true" width="300px">
</div>

With each student submission zip file populated with random content:
<div align="left">
    <img src="docs/images/ex2.PNG?raw=true" width="300px">
</div>

### Identifying project members
```bash
TODO
```

### Organizing project code and reports
```bash
TODO
```


## About Me
My name is [Maxwell Weinzierl](https://personal.utdallas.edu/~maxwell.weinzierl/), and I am a
Natural Language Processing researcher at the Human Technology Research Institute (HLTRI) at the
University of Texas at Dallas. I am currently working on my PhD, which focuses on COVID-19 and
HPV vaccine misinformation, trust, and more on Social Media platforms such as Twitter. I am 
also a Graduate Teaching Assistant for the AI, NLP, and IR classes of Dr. Harabagiu.
