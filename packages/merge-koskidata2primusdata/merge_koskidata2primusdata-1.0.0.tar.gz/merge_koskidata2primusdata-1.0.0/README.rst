merge_koskidata2primusdata
==========================

.. image:: https://img.shields.io/pypi/v/merge_koskidata2primusdata.svg
    :target: https://pypi.python.org/pypi/merge_koskidata2primusdata
    :alt: Latest PyPI version

Utility which merging Koski and Primus CSV reports. Using the Primus card number as identifier.

Usage merge_student_years
-------------------------

Merging Koski student years and primusquery generated CSV reports.

Usage: merge_student_years [OPTIONS] KOSKI_INPUT_PATH OUTPUT_PATH
                           PRIMUS_DATA_FILE

Options:
  -e, --primus_encoding TEXT  [default: utf-8-sig]
  -d, --delimiter TEXT        [default: ;]
  -v, --validation BOOLEAN    [default: True]
  --help                      Show this message and exit.

Usage add_column
----------------

Adding one column outside student registry to end of the merged report.

Usage: add_column [OPTIONS] SOURCE_FILE OUTPUT_PATH

Options:
  -e, --empty_value TEXT
  -c, --primus_encoding TEXT     [default: utf-8-sig]
  -d, --delimiter TEXT           [default: ;]
  -D, --drop_duplicates BOOLEAN  [default: True]
  -v, --validate BOOLEAN         [default: True]
  --help     

Installation
------------
pip install merge-koskidata2primusdata

Requirements
^^^^^^^^^^^^
pandas
click

Compatibility
-------------

Licence
-------

GNU Lesser General Public License v3.0 or later (LGPLv3.0+)

Authors
-------

`merge_koskidata2primusdata` was written by `Pasi Ollikainen <pasi.ollikainen@outlook.com>`_.
