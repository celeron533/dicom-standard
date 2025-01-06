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

A GitHub Actions [workflow][workflow_link] regenerates the JSON files using the most current web version of the DICOM Standard at the beginning of each month. If there are any changes, the updated files are automatically pushed to `master`.

[nema]: http://dicom.nema.org/
[workflow_link]: https://github.com/innolitics/dicom-standard/actions?query=workflow%3Aupdate-standard

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
```shell
    $ make
```
to install and compile everything. Add the `-j` flag to speed this process up
significantly.

### Updating the Standard

To download and parse the most up-to-date web version of the DICOM Standard,
run the following commands in the `dicom_standard` directory:
```shell
    $ make clean
    $ make updatestandard
    $ make
```
Then copy the output to the `standard/` directory:
```shell
    $ cp dist/* ../standard/
```
To download an older version of the DICOM Standard, run
```shell
    $ make updatestandard VERSION=<version>
```
with the year and revision desired, e.g. `2018e`, `2019c`.

WARNING: Differences between previous versions and the current version may cause bugs when used with the current parser library. We recommend forking this repository if you need to use a specific version of the standard.

## Using the Library

Parsing stages are indicated by prefixed names (i.e. `extract_xxx.py` or
`process_xxx.py`) and use a variety of utility functions from `parse_lib.py`
and other `*_utils.py` modules.

### Design Philosophy

The overall data flow of this program takes the following form:

```asciidoc
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
               | CIODs/  |  | CIODs/FG |  | Modules/    |  | Sections |         v             v
               | Modules |  | Macros   |  | Macro Attrs +  +--------+-+     sops.json   attributes.json
               +----+----+  +----+-----+  +------+-----+            |
                    |            |               |                  |
      +-------------+            |               +---------------+  +-----------+
      |             |            |               |               |              |
+-----v-----+  +----v----+  +----v------+  +-----v------+  +-----v------+       |
| Process   |  | Process |  | Process   |  | Preprocess |  | Preprocess |       |
| CIOD/     |  | CIODs   |  | CIOD/FG   |  | Macros     |  | Modules/   |       |
| Module    |  +----+----+  | Macro     |  | Attributes |  | Attributes |       |
| Relations |       |       | Relations |  +-----+------+  +-----+------+       |
+-----+-----+       v       +----+------+        |               |              |
      |        ciods.json        |               +-------+       +-------+      |
      v                          |               |       |       |       |      |
ciod_to_modules.json             |          +----v----+  |  +----v----+  |      |
                                 v          | Process |  |  | Process |  |      |
           ciod_to_func_group_macros.json   | Macros  |  |  | Modules |  |      |
                                 |          +----+----+  |  +----+----+  |      |
                                 |               |       |       |       |      |
                                 |               v       |       v       |      |
                                 |          macros.json  |  modules.json |      |
                                 |           |           |               |      |
                                 |           |   +-------v---+   +-------v---+  |
                                 |           |   | Process   |   | Process   |  |
                                 |           |   | Macro     |   | Module    |  |
                                 |           |   | Attribute |   | Attribute |  |
                                 |           |   | Relations |   | Relations |  |
                                 |           |   +-------+---+   +-------+---+  |
                                 |           |           |               |      |
                                 |           |         +-v---------------v------v-+
                                 |           |         |       Postprocess        |
                                 |           |         |      Add References      +-----------+
                                 |           |         +-+---------------+--------+           |
                                 |           |           |               |                    |
                          +------v-----------v---+     +-v---------------v--------+  +--------v--------+
                          |     Postprocess      <-----+       Postprocess        |  | Save References |
                          | Integrate Functional |     |   Merge Duplicate Nodes  |  +--------+--------+
                          |     Group Macros     <--+  +-------------+------------+           |
                          +-----------+----------+  |                |                        |
                                      |             |                v                        v
                                      v             +----macros_to_attributes.json      references.json
                         modules_to_attributes.json
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

## DICOM Standard Workarounds

Certain parts of the DICOM Standard site cause errors when running the parser, often due to typos or formatting inconsistencies.

When we find one of these issues, we add a hard-coded fix in the relevant file and add a comment starting with 'Standard workaround' that describes the issue and links to its location in the Standard. To be aware when these fixes are obsolete, we add a unit test that fails once the issue no longer exists.

Current standard workarounds (as of rev.2024b):
| *Issue description* | *Workaround location* |
|---|---|
| [Table TID 1004](http://dicom.nema.org/medical/dicom/current/output/chtml/part16/chapter_A.html#sect_TID_1004) has a section URL pattern ("sect_TID_1004") that doesn't exist within the HTML version of the standard | `parse_lib.py` |
| Certain subsections are located within the base section rather than having their own section (C.7.16.2.5.1 should be within C.7.16.2.5, but `sect_C.7.16.2.5.html` is invalid) | `parse_lib.py`<br>`extract_modules_macros_with_attributes.py` |
| \*[The Enhanced MR Color Image IOD](http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.36.4.4.html) references the Enhanced MR Image IOD's functional group macros table instead of having its own (they would be identical tables) | `extract_ciod_func_group_macro_tables.py` |
| \*[Table F.3-1](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_F.3.html#table_F.3-1) has no "Information Entity" column so the href is in the second column | `extract_ciod_module_tables.py` |
| [Table A.89.4-1](https://dicom.nema.org/medical/dicom/2023c/output/chtml/part03/sect_A.89.4.html#table_A.89.4-1) Mismatch of 'Photoacoustic Reconstruction Algorithm' name | `extract_ciod_func_group_macro_tables.py`<br>`parse_lib.py`<br>`process_ciod_func_group_macro_relationship.py` |
| The "Referenced Patient Alias Sequence" attribute is noted to be retired in [Table 6-1](https://dicom.nema.org/medical/dicom/current/output/chtml/part06/chapter_6.html#para_74d743fc-e532-4817-8477-58d1e9a8de57) but is not retired in [Table E.1-1](https://dicom.nema.org/medical/dicom/current/output/html/part15.html#para_26d0b4be-9dae-4b57-ab18-8e524dde7dc1) | `extract_conf_profile_attributes.py` |
| The [Confocal Microscopy Image Functional Group Macros](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.90.html#sect_A.90.1.5) section doesn't have a description, causing the "module_type" value to be None when it should be "Multi-frame" | `extract_ciod_func_group_macro_tables.py` |
| The [Confocal Microscopy Tiled Pyramidal Image Functional Group Macros](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.90.2.5.html#sect_A.90.2.5) section doesn't have a description, causing the "module_type" value to be None when it should be "Multi-frame" | `extract_ciod_func_group_macro_tables.py` |
| [Table A.89.4-1](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.89.4.html#table_A.89.4-1) is missing part of the IOD name ("Photoacoustic" instead of "Photoacoustic Image") in its title | `extract_ciod_func_group_macro_tables.py` |
| The "Confocal Micrsocopy Tiled Pyramidal" IOD Specification in [Table B.5-1](https://dicom.nema.org/medical/dicom/current/output/chtml/part04/sect_B.5.html#table_B.5-1) should include the word "Image" after "Pyramidal" | `extract_sops.py`
| The "Pseudo-color Softcopy Presentation State" IOD Specification in [Table B.5-1](https://dicom.nema.org/medical/dicom/current/output/chtml/part04/sect_B.5.html#table_B.5-1) should have an upper-case "C" in "Color" | `extract_sops.py`

(\*) This issue is not caused by a typo or error in the Standard but rather an exception from the normal format and thus does not have a unit test for a fix.

Fixed workarounds:
| *Issue description* | *Workaround location* | *Fixed as of*
|---|---|---|
| [Table A.39.19-1](http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.35.19.3.html) ends its title with an upper case "S" | `extract_ciod_module_tables.py`<br>`parse_lib.py` | 2023e |
| [Table A.32.9-2](http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.32.9.3.4.html#table_A.32.9-2) has "Functional Groups Macros" in its title while other tables use "Functional Group Macros" | `extract_ciod_func_group_macro_tables.py`<br>`parse_lib.py` | 2023e |
| [Table A.52.4.3-1](http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.52.4.3.html#table_A.52.4.3-1) is missing "Image" from the IOD name portion of the title | `extract_ciod_func_group_macro_tables.py` | 2023e |
| [Table C.8-125](http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.15.3.9.html#table_C.8-125) has an extra "Sequence" in its title (should be "CT X-Ray Details", not "CT X-Ray Details Sequence") | `parse_lib.py` | 2023e |
| [Table A.84.3.2-1](http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.84.3.2.html#table_A.84.3.2-1) contains a macro that has an extra "Macro" in its name ("Frame VOI LUT With LUT Macro") | `process_ciod_func_group_macro_relationship.py` | 2023e |
| [Table C.8.25.16-8](http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.25.16.8.html) has an include statement with an extra hierarchy marker (two instead of one) | `hierarchy_utils.py` | 2023e |
| [Table A.32.10-1](http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.32.10.2.html#table_A.32.10-1) is missing values in the "Information Entity" field of two rows | `process_ciod_module_relationship.py` | 2023e |
| [Table A.35.21-1](http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.35.21.3.html#table_A.35.21-1) contains an upper case "O" in "Frame of Reference", while other tables use the lower case | `process_ciod_module_relationship.py` | 2023e |
| [The File-Set Identification Module](http://dicom.nema.org/dicom/2013/output/chtml/part03/sect_F.3.html#sect_F.3.2.1) has no description paragraph | `extract_modules_macros_with_attributes.py` | 2023e |
| [Table C.8.34.5.1-1](https://dicom.nema.org/medical/dicom/2023c/output/chtml/part03/sect_C.8.34.5.html#table_C.8.34.5.1-1) Macro table 'Photoacoustic Excitation Characteristics Attributes' is not using suffix 'Macro Attributes' | `extract_modules_macros_with_attributes.py`<br>`parse_lib.py` | 2023e |
| \*The "Content Creator's Name" attribute appears twice in [Table C.36.8-1](http://dicom.nema.org/medical/dicom/2019c/output/chtml/part03/sect_C.36.8.html#table_C.36.8-1) with the same hierarchy without a conditional statement | `postprocess_merge_duplicate_nodes.py` | 2023e |
| \*[Table F.3-3](http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_F.3.2.2.html#table_F.3-3) contains a "Record Selection Keys" attribute with an invalid tag ("See F.5") | `preprocess_modules_with_attributes.py` | 2023e |

## Contact

You can contact us directly through our [website][contact_link].

### Reporting Issues and Bugs

If you find a bug or have suggestions for improvement, please open a [GitHub issue][issue_link] or make a [pull request][pr_link].

[issue_link]: https://github.com/innolitics/dicom-standard/issues/new/choose
[pr_link]: https://github.com/innolitics/dicom-standard/pulls
