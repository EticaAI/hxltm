#!/usr/bin/env python3

# testum/de-python/testinfra/test_disciplinam_manuale.py is a port of
# testum/disciplinam-manuale-anglicum.sh

# To output even more verbose results
#     ./testum/de-python/testinfra/test_disciplinam_manuale.py
#
# To test directly
#     pytest -vv ./testum/de-python/testinfra/test_disciplinam_manuale.py

# NOTE: this file require testinfra, https://testinfra.readthedocs.io/en/latest/
#     pip3 install pytest-testinfra

# TODO: https://testinfra.readthedocs.io/en/latest/examples.html
#       Implement things via parameters


# @see https://github.com/amoffat/sh
# @see https://amoffat.github.io/sh/
# @see https://blog.esciencecenter.nl/testing-shell-commands-from-python-2a2ec87ebf71
# @see https://github.com/NLeSC/python-template/blob/master/tests/test_project.py

import os
import sys
import pytest

# import pytest.testinfra

# TODO: fix this on tox
def test_disciplinam_manuale_hxltmcli_hxltm_csv(host):
    # host.run('cd testum/')
    # cmd = host.run("hxltmcli hxltm-exemplum-linguam.tm.hxl.csv")
    # cmd = host.run("cd testum/; ls -l")
    # cmd = host.run("cd testum/; ls")
    cmd = host.run("hxltmcli --help")
    # cmd = host.run("pwd")
    # cmd = host.run("hxltmcli testum/hxltm-exemplum-linguam.tm.hxl.csv")
    # cmd2 = host.run("cat testum/hxltm-exemplum-linguam.tm.hxl.csv | hxltmcli")
    # cmd = host.run("pwd")

    assert cmd.succeeded
    # assert cmd2.succeeded

    # assert print(cmd)

# TODO: HXLTM-ASA


# def test_disciplinam_manuale_hxltmcli_csv_3(host):
#     # host.run('cd testum/')
#     # cmd = host.run("hxltmcli hxltm-exemplum-linguam.tm.hxl.csv")
#     # cmd = host.run("cd testum/; ls -l")
#     cmd = host.run(
#         "cd testum/; hxltmcli hxltm-exemplum-linguam.tm.hxl.csv --objectivum-CSV-3")
#     # cmd = host.run(
#     #     "cd testum/; hxltmcli hxltm-exemplum-linguam.tm.hxl.csv --objectivum-CSV-3 --fontem-linguam por-Latn@pt --objectivum-linguam spa-Latn@es")
#     # cmd = host.run("pwd")

#     assert cmd.succeeded
