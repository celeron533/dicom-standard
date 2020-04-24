[![Travis CI build status](https://img.shields.io/travis/innolitics/dicom-standard?label=Travis%20CI&logo=travis)](https://travis-ci.org/innolitics/dicom-standard)
[![update-standard workflow status](https://github.com/innolitics/dicom-standard/workflows/update-standard/badge.svg)](https://github.com/innolitics/dicom-standard/actions?query=workflow%3Aupdate-standard)
[![PyPI version](https://img.shields.io/pypi/v/dicom-standard?label=PyPI&color=blue&logo=pypi)](https://pypi.org/project/dicom-standard/)

# DICOM Standard Parser

This program parses the web version of the [DICOM Standard][nema] into human
and machine-friendly JSON files. The purpose of these JSON files is twofold:

1. To provide a standardized and machine-readable way to access DICOM Standard
   information for software applications

2. To provide a logical model for the relationships between cross-referenced
   sections in the DICOM Standard

The finalized JSON output of this program is in the `standard` directory at the
top level of this project.

[nema]: http://dicom.nema.org/

## Usage

The DICOM Standard Parser is useful for modeling and understanding properties of the various abstractions defined by the DICOM Standard (IODs, modules, attributes, etc.) as well as the relationships between them.

The raw HTML or XML represents the DICOM Standard as a document but the data isn't easily machine-readable. We process the data from the HTML format into organized JSON files which follow a set of formatting guidelines and contain natural keys to represent relationships between abstractions.

To find or work with a smaller amount of data, e.g. a single IOD, the [DICOM Standard Browser][standard_browser] may be appropriate.

[standard_browser]: https://dicom.innolitics.com/ciods

## Installation

Install the latest release with `pip install dicom-standard`.

To download a specific JSON file, run `curl https://raw.githubusercontent.com/innolitics/dicom-standard/master/standard/<filename> -o <destination>`.

[curl]: https://curl.haxx.se/

## JSON Data Format

The generated JSON files conform to these formatting rules:

- JSON files representing objects are lists of dictionaries that each contain information relevant to the object.
- JSON files containing relational data between objects contain "foreign keys" to the relevant objects. These field names end with `Id`, e.g. `ciodId` and `moduleId`.

Occasionally, files may deviate from this format when there is a very compelling reason. For example, `references.json` should be a list of reference objects where the href link is the `id` for each object. However, since almost every use case for `references.json` will use the href as a lookup, it makes more sense for the file to be set up as an object containing href to HTML pairs.

Applications that use the JSON files from this repository may need to re-organize data. A separate script must be written to join data from multiple tables into one file or prune out unnecessary fields.

## JSON Data Guarantees

The JSON generated by this program adheres to the following four rules:

1. New fields may be added
2. Bugs or incorrect data will be fixed as the standard changes
3. No fields are removed, maintaining backwards compatibility
4. The shape and organization of the JSON files will remain the same

The JSON files can be viewed [here][json_link].

[json_link]: https://github.com/innolitics/dicom-standard/tree/master/standard

## Users

- [DICOM Standard Browser](https://dicom.innolitics.com) by [Innolitics](https://innolitics.com/)

Please [contact us][contact_link] if you use this software and would like your name or company listed here.

[contact_link]: https://innolitics.com/about/contact/

## Current Status

This program currently parses the DICOM Standard sections related to
Information Object Definitions, modules, and attributes, as well as
cross-referenced sections in other parts of the standard. This translates to
the following sections:

Completely processed:

- PS3.3
- PS3.4
- PS3.6

Processed for references:

- PS3.15
- PS3.16
- PS3.17
- PS3.18

## Development Setup

The Python scripts used to generate the JSON files are designed to be as
extensible as possible. If you want to run the code yourself or configure your
own custom parsing stage, you'll need the following system-level dependencies:

- Python 3.7
- Make + Unix tools

You will probably also want to setup a "virtual environment" (e.g. using Conda,
or Pyenv + Virtualenv) to install the project dependencies into.  Once you are
in your "virtual environment", you can run:

    $ make

to install and compile everything. Add the `-j` flag to speed this process up
significantly.

### Updating the Standard

To download and parse the most up-to-date web version of the DICOM Standard,
run the following commands:

    $ make clean
    $ make updatestandard
    $ make

To download an older version of the DICOM Standard, run

    $ make updatestandard VERSION=<version>

with the year and revision desired, e.g. `2018e`, `2019c`.

WARNING: Differences between previous versions and the current version may cause bugs when used with the current parser library. We recommend forking this repository if you need to use a specific version of the standard.

## Using the Library

Parsing stages are indicated by prefixed names (i.e. `extract_xxx.py` or
`process_xxx.py`) and use a variety of utility functions from `parse_lib.py`
and other `*_utils.py` modules.

### Design Philosophy

The overall data flow of this program takes the following form:

```
          extract                      (post)process
Raw HTML ---------> JSON intermediate ---------------> JSON final

```

During this process, the following invariants are maintained:

- Each step in the parsing process is classified as either an "extract" stage,
  or a "process" stage.
- Stages are python scripts that take one or more files as inputs, and write
  their output to standard out.
- "Extract" stages takes one more more HTML input files and print out JSON.
- "Process" stages take one or more JSON files as inputs and print out JSON.

In this way, raw HTML is not touched by any stage other than `extract_*.py`,
and successive processing steps use increasingly refined JSON.

### Parser Stages

A map of all extraction and processing pathways is shown below:

```
                                      +-------+             +----------+    +-------+     +-------+
                                      | PS3.3 |             | Other    |    | PS3.4 |     | PS3.6 |
                                      +---+---+             | DICOM    |    +---+---+     +---+---+
                                          |                 | Sections |        |             |
                                          |                 +-----+----+        |             |
                                          |                       |        +----v----+  +-----v------+
                   +-------------+--------+------+-------------+  |        | Extract |  | Extract    |
                   |             |               |             |  |        | SOPs    |  | Attributes |
               +---v-----+  +----v-----+  +------v------+  +---v--v---+    +----+----+  +-----+------+
               | Extract |  | Extract  |  | Extract     |  | Extract  |         |             |
               | CIODs/  |  | CIODs/FG |  | Modules/    |  | Sections |         |             |
               | Modules |  | Macros   |  | Macro Attrs |  +--------+-+         v             v
               +----+----+  +----+-----+  +------+-----+            |       sops.json   attributes.json
                    |            |               |                  |
      +-------------+            |               +---------------+  +-----------+
      |             |            |               |               |              |
+-----v-----+  +----v----+  +----v------+  +-----v------+  +-----v------+       |
| Process   |  | Process |  | Process   |  | Preprocess |  | Preprocess |       |
| CIOD/     |  | CIODs   |  | CIOD/FG   |  | Modules/   |  | Macros/    |       |
| Module    |  +----+----+  | Macro     |  | Attributes |  | Attributes |       |
| Relations |       |       | Relations |  +-----+------+  +-----+------+       |
+-----+-----+       |       +----+------+        |               |              |
      |             v            |               +-------+       +-------+      |
      |        ciods.json        |               |       |       |       |      |
      v                          |          +----v----+  |  +----v----+  |      |
ciod_to_modules.json             |          | Process |  |  | Process |  |      |
                                 v          | Modules |  |  | Macros  |  |      |
           ciod_to_func_group_macros.json   +----+----+  |  +----+----+  |      |
                                                 |       |       |       |      |
                                                 |       |       |       |      |
                                                 v       |       v       |      |
                                            modules.json |  macros.json  |      |
                                                         |               |      |
                                                 +-------v---+   +-------v---+  |
                                                 | Process   |   | Process   |  |
                                                 | Module    |   | Macro     |  |
                                                 | Attribute |   | Attribute |  |
                                                 | Relations |   | Relations |  |
                                                 +-------+---+   +-------+---+  |
                                                         |               |      |
                                                       +-v---------------v------v-+
                                                       |        Postprocess       |
                                                       |      Add References      |
                                                       +-----+-------+------+-----+
                                                             |       |      |
                                                    +--------+       |      +--------+
                                                    |                v               |
                                                    |    macros_to_attributes.json   |
                                                    v                                v
                                         modules_to_attributes.json           references.json
```

To update the parser map, please use [ASCIIFlow][asciiflow].

[asciiflow]: http://asciiflow.com/

## Testing

To run the full test suite, install and run [`tox`][tox].

To run a specific test, run `tox -e <testenv>`. Test environments include:

- `flake8`: check and enforce code style and format
- `mypy`: validate type hints
- `pytest`: run a set of unit and end-to-end tests
- `build-dist`: test building the backend into source and binary distributions

[tox]: https://pypi.org/project/tox/

## Contact

You can contact us directly through our [website][contact_link].

### Reporting Issues and Bugs

If you find a bug or have suggestions for improvement, please open a [GitHub issue][issue_link] or make a [pull request][pr_link].

[issue_link]: https://github.com/innolitics/dicom-standard/issues/new/choose
[pr_link]: https://github.com/innolitics/dicom-standard/pulls
