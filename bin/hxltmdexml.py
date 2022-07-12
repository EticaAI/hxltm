#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  hxltmdexml
#
#         USAGE:  Translation Memory eXchange format (TMX): -> HXLTM:
#                     hxltmdexml fontem.tmx objectivum.tm.hxl.csv
#                     cat fontem.tmx | hxltmdexml > objectivum.tm.hxl.csv
#
#                 TBX-Basic: TermBase eXchange (TBX) Basic: -> HXLTM:
#                     hxltmdexml fontem.tbx objectivum.tm.hxl.csv
#                     cat fontem.tbx | hxltmdexml > objectivum.tm.hxl.csv
#
#   DESCRIPTION:  hxltmdexml is an (not feature-by-feature) conversor
#                 from some XML formats to HXLTM tabular working file.
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - python3
#                     - defusedxml (https://github.com/tiran/defusedxml)
#                       - pip3 install pyyaml
#          BUGS:  ---
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:
#                 <@TODO: put additional non-anonymous names here>
#
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication OR Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v0.8.9
#       CREATED:  2021-07-24 00:04 UTC v0.1.0 de hxl2example
#      REVISION:  2021-07-24 17:49 UTC v0.2.0 hxltmdexml at least read XML
#                 2021-07-25 23:28 UTC v0.5.0 XLIFF 1.2 and XLIFF 2.1 (MVP)
#                 2021-07-28 22:01 UTC v0.7.0 TBX-IATE (MVP), TMX (MVP)
#                 2021-11-06 21:19 UTC v0.8.0 Fix cli importing; more stable
#                 2021-11-17 02:37 UTC v0.8.9 Use cor.hxltm.215.yml
# ==============================================================================
"""hxltmdexml.py: Multilingual Terminology in Humanitarian Language Exchange
(HXLTM) de XML

_[eng-Latn]

Crash course from names in Latin to English
----------

- datum:
    - Dataset
- columnam (or crudum columnam):
    - Column, spreadsheet column, variable (of a item)
- līneam (or crudum līneam):
    - row, spreadsheet row, line (used mostly for 'crudum rem', raw item)
- rem:
    - Thing (generic)
- conceptum
    - Concept (used on HXLTM to diferenciate what is translation, rem, from
      concept that applies to all language variants of the sabe thing)
- fontem:
    - Source
- objectīvum:
    - Objective, target (as in target language, output archive)
- linguam:
    - Language, natural language
- bilingue
    - bilingual (as used on operations with source to target language in XLIFF)
- multiplum linguam
    - 1 to n languages (as used on operations that work with many languages
      like TMX and TBX)
- collēctiōnem:
    - collection, List, array (not sure if exist better naming in Latin, sorry)
- obiectum
    - Object (or Python Dict)
- Caput
    - Header
- Vēnandum īnsectum
    - Debugging
- 'Exemplōrum gratiā (et Python doctest, id est, testum automata)'
    - 'For example (and python doctest, that is, automated testing)'
    - @see https://docs.python.org/3/library/doctest.html
        - python3 -m doctest hxltmcli-fork-from-marcus.py
        - python3 -m doctest hxlm/core/bin/hxltmcli.py

Some other very frequent generic terms:

- ad:
    - @see https://en.wiktionary.org/wiki/ad#Latin
        - (direction) toward, to
        - up to (indicating direction upwards)
        - in consequence of
        - for, to, toward (indicating purpose or aim)
        - in order to, to, for (indicating means)
        - (...)
- de:
    - @see https://en.wiktionary.org/wiki/de#Latin
        - of, concerning, about
        - from, away from, down from, out of
- in:
    - @see https://en.wiktionary.org/wiki/in#Latin
        - toward, towards, against, at
        - until, for
        - about
        - according to

> Tips:
> - HXL-CPLP-Vocab_Auxilium-Humanitarium-API spreadsheet have additional terms
> - Google _wiktionary term-in-english_. Sometimes Google Translate will
>   give the perfect term, but to keep consistent, we use:
>    - Accusative
>        - Singular
>            - Neuter (You know, inclusive language)
> - 'Marcus loves/likes his dog', in Latin (same meaning different emphasis):
>    - Marcus canem amat.
>    - Canem Marcus amat.
>    - Amat canem Marcus.
>    - Marcus amat canem.
>    - Canem amat Marcus.
>    - Amat Marcus canem.
>    - Marcum canis amat.
>    - Canis Marcum amat.
>    - Amat canis Marcum.
>    - Marcum amat canis.
>    - Canis amat Marcum.
>    - Amat Marcum canis.
> - Latin, while very expressive/verbose language (and great to use on
>   ontologies, naming animals, etc, and this is the reason to use a few terms
>   in Latin on hxltmcli.py), was not what 'the people' used because was
>   hard even for the first class citizen with elite education 2000 years ago.
>   - Most example usages with HXLTM will use the 'prestige dialect' for a
>     ISO 15924 script (like translate from lat-Latn to ara-Arab, zho-Hant,
>     rus-Cyrl, and etc...) even when in fact we, 'the people', will use
>     more specific language/dialects, like por-Latn.

Missing 'good' Latin terms to express meaning in English (for software)
----------

- array, list
    - @see https://en.wiktionary.org/wiki/array
    - Sometimes we use 'Python List' as in
        - "Rem collēctiōnem, id est, Python List"
- output (preferable some short word, not like prōductiōnem)
    - @see https://en.wiktionary.org/wiki/output#English
- input
    - @see https://en.wiktionary.org/wiki/input

To Do
---------
- Improve the terms used for 'questions', like
  'quid'/ 'quod'
    - @see https://dcc.dickinson.edu/grammar/latin/questions


[eng-Latn]_
"""

# TODO: since this commit an error with syntax is breaking using on python 3.7
#       https://github.com/EticaAI/hxltm/runs/4343555339?check_suite_focus=true
#       This needs better check later if still persists or is false positive

# import xml.etree.ElementTree as et
import sys
import os
import logging
import argparse
from pathlib import Path
import re
# import xml.etree.ElementTree as ET
import xml.etree.ElementTree as XMLElementTree

from importlib.metadata import version
# from pkg_resources import parse_version

import csv
# import tempfile

from dataclasses import dataclass, InitVar
from typing import (
    Any,
    Dict,
    List,
    # TextIO,
    Type,
    Union,
)

from functools import reduce
from collections import OrderedDict

import yaml

# # @see https://github.com/HXLStandard/libhxl-python
# #    pip3 install libhxl --upgrade
# # Do not import hxl, to avoid circular imports
# import hxl.converters
# import hxl.filters
# import hxl.input

# @see https://github.com/rspeer/langcodes
# pip3 install langcodes
# import langcodes

__version__ = "0.9.2rc2"

# _[eng-Latn]
# Note: If you are doing a fork and making it public, please customize
# __SYSTEMA_VARIANS__, even if the __version__ keeps the same
# [eng-Latn]_
__SYSTEMA_VARIANS__ = "hxltmdexml.py;EticaAI+voluntārium-commūne"
# Trivia:
# - systēma, https://en.wiktionary.org/wiki/systema#Latin
# - variāns, https://en.wiktionary.org/wiki/varians#Latin
# - furcam, https://en.wiktionary.org/wiki/furca#Latin
# - commūne, https://en.wiktionary.org/wiki/communis#Latin
# - voluntārium, https://en.wiktionary.org/wiki/voluntarius#Latin

__DESCRIPTIONEM_BREVE__ = """
_[eng-Latn]
hxltmdexml {0} is an example of implementation of the
Multilingual Terminology in Humanitarian Language Exchange (HXLTM)
focused on convert XML files to the pivot format HXLTM.
[eng-Latn]_"
""".format(__version__)

__ATTRIBUTUM_OPTIONEM__ = {
    # No annotationem (text notes) at concept level: please use meta_conceptum
    'annotationem': [
        '#meta+linguam+__linguam__+annotationem',
        '#meta+terminum+__linguam__+annotationem',
    ],
    'annotationem_linguam': ['#meta+linguam+__linguam__+annotationem'],
    'annotationem_terminum': ['#meta+terminum+__linguam__+annotationem'],
    'codicem': ['#item+conceptum+codicem'],
    'codicem_conceptum': [
        '#item+conceptum+codicem'
    ],
    'dominium': ['#item+conceptum+dominium'],
    'indicem_de_terminum': ['#item+conceptum+indicem_de_terminum'],
    'meta': [
        '#meta+conceptum',
        '#meta+linguam+__linguam__',
        '#meta+terminum+__linguam__',
    ],
    'meta_conceptum': ['#meta+conceptum'],
    'meta_linguam': ['#meta+linguam+__linguam__'],
    'meta_terminum': ['#meta+terminum+__linguam__'],
    # __nomen_breve: 'rem__L__'
    'rem': ['#item+terminum+__linguam__+rem'],
}
__ATTRIBUTUM_DEFALLO__ = [
    # 'codicem' # hardcoded, cannot be removed
    # 'rem' # hardcoded, cannot be removed
    'indicem_de_terminum',
    'meta'
]

# tag::epilogum[]
__EPILOGUM__ = """
Exemplōrum gratiā:

XML Localization Interchange File Format (XLIFF) v2.1+: -> HXLTM (bilinguam):
    hxltmdexml fontem.xlf objectivum.tm.hxl.csv

XML Localization Interchange File Format (XLIFF) v1.2: -> HXLTM (bilinguam):
    hxltmdexml fontem.xlf objectivum.tm.hxl.csv

Translation Memory eXchange format (TMX): -> HXLTM:
    hxltmdexml fontem.tmx objectivum.tm.hxl.csv

TBX-Basic: TermBase eXchange (TBX) Basic: -> HXLTM:
    hxltmdexml fontem.tbx objectivum.tm.hxl.csv

TBX-IATE (id est, https://iate.europa.eu/download-iate) -> HXLTM (por-Latn@pt)

    zcat IATE_download.zip | hxltmdexml --agendum-linguam por-Latn@pt
    cat IATE_export.tbx | hxltmdexml --agendum-linguam por-Latn@pt

TBX-IATE (id est, https://iate.europa.eu/download-iate) -> HXLTM (...)

    hxltmdexml IATE_export.tbx IATE_export.hxltm.csv \\
        --agendum-linguam bul-Latn@bg \\
        --agendum-linguam ces-Latn@cs \\
        --agendum-linguam dan-Latn@da \\
        --agendum-linguam dut-Latn@nl \\
        --agendum-linguam ell-Latn@el \\
        --agendum-linguam eng-Latn@en \\
        --agendum-linguam est-Latn@et \\
        --agendum-linguam fin-Latn@fi \\
        --agendum-linguam fra-Latn@fr \\
        --agendum-linguam ger-Latn@de \\
        --agendum-linguam ger-Latn@de \\
        --agendum-linguam gle-Latn@ga \\
        --agendum-linguam hun-Latn@hu \\
        --agendum-linguam ita-Latn@it \\
        --agendum-linguam lav-Latn@lv \\
        --agendum-linguam lit-Latn@lt \\
        --agendum-linguam mlt-Latn@mt \\
        --agendum-linguam pol-Latn@pl \\
        --agendum-linguam por-Latn@pt \\
        --agendum-linguam ron-Latn@ro \\
        --agendum-linguam slk-Latn@sk \\
        --agendum-linguam slv-Latn@sl \\
        --agendum-linguam spa-Latn@es \\
        --agendum-linguam swe-Latn@sv

"""
# end::epilogum[]

# import tempfile


# @see https://github.com/hugapi/hug
#     pip3 install hug --upgrade
# import hug

# In Python2, sys.stdin is a byte stream; in Python3, it's a text stream
STDIN = sys.stdin.buffer

_HOME = str(Path.home())

# cor.hxltm.215.ext:
# 1. HXLTM_RUNNING_DIR ; defallo .
# 2. HXLTM_DORMUM      ; defallo ~/.config/hxlm/cor.hxltm.215.ext
# 3. HXLTM_SYSTEMA_DIR  ; defallo hxltmcli.py dir

# _[eng-Latn]
# Environment variables HXLTM_DORMUM (for default search place for
# configurations) HXLTM_TESTUM (for default place to search for test
# files) can be manually configured.
# [eng-Latn]_
HXLTM_DORMUM = os.getenv('HXLTM_DORMUM', _HOME + '/.config/hxltm')
HXLTM_TESTUM = os.getenv(
    'HXLTM_TESTUM', HXLTM_DORMUM + '/testum')
# TODO: make HXLTM_TESTUM instalable as python package

# systēma

HXLTM_SYSTEMA_DIR = str(Path(__file__).parent.resolve())
HXLTM_RUNNING_DIR = str(Path().resolve())

# De Python Constants
# modus_operandi values
# https://en.wiktionary.org/wiki/multilingual#English
MULTIPLUM_LINGUAM: int = 0
# mono, https://en.wiktionary.org/wiki/mono#English
# ūnum, https://en.wiktionary.org/wiki/mono#English
UNUM_LINGUAM: int = 1
# bīnum, https://en.wiktionary.org/wiki/binus#Latin
BINUM_LINGUAM: int = 2

# modus_operandi_defallo: List[int] = [MULTIPLUM_LINGUAM, BINUM_LINGUAM]


class HXLTMDeXMLCli:
    """
    HXLTMDeXMLCli is a classe to export already HXLated data in the format
    example.
    """

    EXIT_OK = 0
    EXIT_ERROR = 1
    EXIT_SYNTAX = 2

    def __init__(self):
        """
        Constructs all the necessary attributes for the HXLTMDeXMLCli object.
        """
        self.hxlhelper = None
        self.args = None

        self._ontologia: Type['HXLTMOntologia'] = None

    def _initiale(self, pyargs):
        """Trivia: initiāle, https://en.wiktionary.org/wiki/initialis#Latin
        """

        conf = HXLTMUtil.load_hxltm_options(
            pyargs.archivum_configurationem,
            pyargs.venandum_insectum
        )

        self._ontologia = HXLTMOntologia(conf)

    def make_args(self):
        """make_args
        """

        # self.hxlhelper = HXLUtils()
        self.hxlhelper = HXLUtilsDeXML()
        parser = self.hxlhelper.make_args(
            description=__DESCRIPTIONEM_BREVE__,
            epilog=__EPILOGUM__
        )

        parser.add_argument(
            '--agendum-linguam', '-AL',
            help='List of working languages. Required for '
            'multilinguam formats (like TBX) both to '
            'avoid scan the source file and to be sure about HXL attributes '
            'of the output format. '
            'Example I (Latin and Arabic): lat-Latn@la,arb-Arab@ar . '
            'Example II (TBX IATE, es,en,fr,la,pt,mul): '
            'spa-Latn@es,eng-Latn@en,fra-Latn@fr,lat-Latn@la,por-Latn@pt,'
            'mul-Zyyy',
            metavar='agendum_linguam',
            action='append',
            nargs='?'
        )

        parser.add_argument(
            '--agendum-attributum', '-AA',
            help='(draft, not fully implemented). Additional attributes '
            'to import/export. Required for some '
            'multilinguam formats (like TBX) both to '
            'avoid scan the source file and to be sure about HXL attributes '
            'of the output format. '
            'Default: {0}. Options: [{1}]'.format(
                ','.join(__ATTRIBUTUM_DEFALLO__),
                ' '.join(__ATTRIBUTUM_OPTIONEM__.keys())
            ),
            metavar='agendum_attributum',
            action='append',
            nargs='?',
        )

        parser.add_argument(
            '--fontem-linguam', '-FL',
            help='',
            # dest='fontem_linguam',
            metavar='fontem_linguam',
            action='store',
            # default='lat-Latn@la',
            default=None,
            nargs='?'
        )

        parser.add_argument(
            '--objectivum-linguam', '-OL',
            help='',
            metavar='objectivum_linguam',
            action='store',
            # default='arb-Arab@ar',
            default=None,
            nargs='?'
        )

        # https://hdp.etica.ai/ontologia/cor.hxltm.215.yml
        parser.add_argument(
            '--archivum-configurationem',
            help='Path to custom configuration file (The cor.hxltm.215.yml)',
            action='store_const',
            const=True,
            default=None
        )

        parser.add_argument(
            '--venandum-insectum-est', '--debug',
            help='Enable debug? Extra information for program debugging',
            metavar="venandum_insectum",
            dest="venandum_insectum",
            action='store_const',
            const=True,
            default=False
        )

        # versiōnem, https://en.wiktionary.org/wiki/versio#Latin
        parser.add_argument(
            '--versionem', '--version',
            help='Output versions (JSON output)',
            metavar="venandum_insectum",
            dest="versionem",
            action='store_const',
            const=True,
            default=False
        )

        self.args = parser.parse_args()

        return self.args

    def execute_cli(
        self, pyargs,
        stdin=STDIN,
        stdout=sys.stdout,
        _stderr=sys.stderr
    ):
        """
        The execute_cli is the main entrypoint of HXLTMDeXMLCli.
        """

        self._initiale(pyargs)

        if pyargs.versionem:
            # print(sys.argv[0] + " " + __version__
            # + "[" + __SYSTEMA_VARIANS__ + "]")
            print(sys.argv[0] + " " + __version__)

            print('libhxl {0}'.format(version('libhxl')))
            sys.exit(0)

        fontem_archivum = pyargs.infile if pyargs.infile else stdin
        objectvum_archivum = pyargs.outfile if pyargs.outfile else stdout

        agendum_linguam = []
        if pyargs.agendum_linguam:
            for item in pyargs.agendum_linguam:
                # print('item', item)
                rem = item.split(',')
                for resultatum in rem:
                    if resultatum not in agendum_linguam:
                        agendum_linguam.append(resultatum)

        agendum_attributum = []
        if pyargs.agendum_attributum:
            for item in pyargs.agendum_attributum:
                # print('item', item)
                rem = item.split(',')
                for resultatum in rem:
                    if resultatum not in agendum_attributum:
                        agendum_attributum.append(resultatum)
        else:
            agendum_attributum = __ATTRIBUTUM_DEFALLO__

        # print('pyargs.agendum_attributum', pyargs.agendum_attributum)
        # print('agendum_attributum', agendum_attributum)

        dexml = HXLTMdeXML(
            self._ontologia,
            fontem_archivum,
            objectvum_archivum,
            # agendum_linguam=pyargs.agendum_linguam,
            agendum_linguam=agendum_linguam,
            agendum_attributum=agendum_attributum,
            fontem_linguam=pyargs.fontem_linguam,
            objectivum_linguam=pyargs.objectivum_linguam,
        )

        return dexml.in_archivum()


class HXLTMdeXML:
    """HXLTM de  XML

    Trivia:
        - HXLTM:
        - HXLTM, https://hdp.etica.ai/hxltm
            - HXL, https://hxlstandard.org/
            - TM, https://www.wikidata.org/wiki/Q333761

    Intrōductōrium cursum de Latīnam linguam (breve glōssārium):
        - archīvum, https://en.wiktionary.org/wiki/archivum
        - datum, https://en.wiktionary.org/wiki/datum#Latin
        - contextum, https://en.wiktionary.org/wiki/contextus#Latin
        - corporeum, https://en.wiktionary.org/wiki/corporeus#Latin
        - collēctiōnem, https://en.wiktionary.org/wiki/collectio#Latin
            - id est: Python List
        - dē, https://en.wiktionary.org/wiki/de#Latin
        - errōrem, https://en.wiktionary.org/wiki/error#Latin
        - fīnāle, https://en.wiktionary.org/wiki/finalis#Latin
        - fōrmātum, https://en.wiktionary.org/wiki/formatus#Latin
        - fontem, https://en.wiktionary.org/wiki/fons#Latin
        - 'id est', https://en.wiktionary.org/wiki/id_est
        - initiāle, https://en.wiktionary.org/wiki/initialis#Latin
        - locum, https://en.wiktionary.org/wiki/locum#Latin
        - objectīvum, https://en.wiktionary.org/wiki/objectivus#Latin
        - resultātum, https://en.wiktionary.org/wiki/resultatum
        - rādīcem, https://en.wiktionary.org/wiki/radix#Latin

    Speciāle verbum in HXLTM:
        - 'Exemplōrum gratiā (et Python doctest, id est, testum automata)'
            - Exemplōrum gratiā
              - https://en.wikipedia.org/wiki/List_of_Latin_phrases_(full)
            - 'Python doctest' (non Latīnam)
                -https://docs.python.org/3/library/doctest.html
    """

    # Trivia:
    # - exitum, https://en.wiktionary.org/wiki/exitus#Latin
    # - errōrem, https://en.wiktionary.org/wiki/error#Latin
    # - syntaxim, https://en.wiktionary.org/wiki/syntaxis#Latin
    # - corrēctum, https://en.wiktionary.org/wiki/correctus#Latin
    #     - correct (de Anglicum)
    #         - OK (de anglicum),
    #            - https://en.wiktionary.org/wiki/OK#English
    #            - https://en.wiktionary.org/wiki/oll_korrect#English
    EXITUM_CORRECTUM = 0
    EXITUM_ERROREM = 1
    EXITUM_SYNTAXIM = 2

    # import xml.etree.ElementTree as XMLElementTree
    # arborem: Type['XMLElementTree'] = None
    arborem = None
    arborem_radicem = None
    # arborem: Dict = None
    radicem_signum: str = ''  # tmx, xliff, martif, tbx
    xml_typum = None
    # referēns, https://en.wiktionary.org/wiki/referens#Latin
    xml_referens = None
    in_formatum = None

    # iterātiōnem, https://en.wiktionary.org/wiki/iteratio#Latin

    iteratianem = None

    objectvum_archivum = sys.stdout,
    _agendum_linguam: Type[List['HXLTMLinguam']] = []
    _agendum_attributum: Type[List[str]] = []
    _fontem_linguam: Type['HXLTMLinguam'] = None
    _objectivum_linguam: Type['HXLTMLinguam'] = None

    # TODO: _modus_operandi
    _modus_operandi: List[int] = [
        MULTIPLUM_LINGUAM,
        BINUM_LINGUAM
    ]

    # _agendum_linguam [] []

    def __init__(
        self,
        ontologia: Type['HXLTMOntologia'],
        fontem_archivum=sys.stdin.buffer,
        objectvum_archivum=sys.stdout,
        # agendum_linguam: Type[List['HXLTMLinguam']] = None,
        agendum_linguam: List[str] = None,
        agendum_attributum: List[str] = None,
        fontem_linguam: str = None,
        objectivum_linguam: str = None,
    ):
        """__init__

        Args:
            ontologia (HXLTMOntologia): ontologia
            fontem_archivum (): fomtem archīvum
            objectvum_archivum (): objectīvum archīvum
            agendum_linguam (List): objectīvum archīvum
        """

        self._ontologia = ontologia

        if fontem_archivum:
            self.fontem_archivum = fontem_archivum
        else:
            self.fontem_archivum = sys.stdin.buffer

        if objectvum_archivum:
            self.objectvum_archivum = objectvum_archivum
            # if isinstance(self.objectvum_archivum, TextIO):
            if isinstance(self.objectvum_archivum, str):
                self.objectvum_archivum = \
                    open(self.objectvum_archivum, 'w')
        else:
            self.objectvum_archivum = sys.stdout

        if agendum_linguam:
            for item in agendum_linguam:
                self._agendum_linguam.append(HXLTMLinguam(item))

        if agendum_attributum:
            self._agendum_attributum = agendum_attributum

        self._fontem_linguam = fontem_linguam
        # if fontem_linguam:
        #     self._fontem_linguam = HXLTMLinguam(fontem_linguam)

        self._objectivum_linguam = objectivum_linguam
        # if objectivum_linguam:
        #     self._objectivum_linguam = HXLTMLinguam(objectivum_linguam)

        self.in_formatum = XMLInFormatumHXLTM(
            self._ontologia,
            self._agendum_linguam,
            self._agendum_attributum,
            # self._fontem_linguam,
            # self._objectivum_linguam
        )

        # TODO: test what happens if input is not XML or was compressed
        #       them deal with message errors for non-XML already on
        #       initialization
        self.iteratianem = XMLElementTree.iterparse(
            source=self.fontem_archivum,
            events=('start', 'end')
        )

        self._initiale()

    def _initiale(self):
        """initiāle, https://en.wiktionary.org/wiki/initialis#Latin
        """

        # print(self.iteratianem)
        # ēventum, https://en.wiktionary.org/wiki/eventus#Latin
        # nōdum, https://en.wiktionary.org/wiki/nodus#Latin
        _eventum, nodum = next(self.iteratianem)

        # print('_initiale {0}, {1}, {2}'.format(
        #     _eventum, nodum, nodum.attrib))

        # {urn:iso:std:iso:30042:ed-2}tbx -> tbx
        self.radicem_signum = HXLTMUtil.xml_clavem_breve(nodum.tag)
        # TODO: implement at least type and version from root tag

        self.xml_typum = self._ontologia.quod_xml_typum(
            self.radicem_signum,
            nodum.attrib
        )

        if self.xml_typum['linguam_fontem']:
            self.in_formatum.definitionem_linguam_fontem(
                self.xml_typum['linguam_fontem']
            )

        if self.xml_typum['linguam_objectivum']:
            self.in_formatum.definitionem_linguam_objectivum(
                self.xml_typum['linguam_objectivum']
            )

        self.xml_referens = self._ontologia.quod_xml_typum_tag(
            self.xml_typum['hxltm_normam']
        )

        # _eventum2, nodum2 = next(self.iteratianem)
        # print('_initiale2 {0}, {1}'.format(_eventum2, nodum2))

        # print('zzzetas', self.xml_typum)

    def _de_commune_xml(self, ontologia_de_xml: Dict):
        """HXLTM de commūne HXL

        Trivia:
            - XML, https://www.w3.org/XML/
            - commūne, https://en.wiktionary.org/wiki/communis#Latin

        Args:
            ontologia_de_xml (Dict):
                *.hxltm.yml:ontologia.normam.[formatum].de_xml

        Returns:
            [type]: [description]
        """

        # pylint: disable=too-many-locals,too-many-branches,invalid-name

        # ___________________________________________________________________ #
        #                                                                     #
        #   (\                         Ontologia libellam                     #
        #   \'\                        - I glossarium                         #
        #    \'\     __________        - II conceptum                         #
        #    / '|   ()_________)       - III linguam                          #
        #    \ '/    \ ~~~~~~~~ \      - IV terminum                          #
        #      \       \ ~~~~~~   \                                           #
        #      ==).      \__________\  Contextum de valōrem                   #
        #     (__)       ()__________) - commūne                              #
        #                              - multum linguam                       #
        #                              - linguam fontem et linguam objectīvum #
        #  - signum                                                           #
        #    - XML tag                                                        #
        #  - de_attributum                                                    #
        #    - (of) XML attribute                                             #
        # ___________________________________________________________________ #

        # I glossarium ------------------------------------------------------ #
        # Contextum: commūne ..................................................

        resultatum_csv = csv.writer(
            self.objectvum_archivum,
            delimiter=',',
            quoting=csv.QUOTE_MINIMAL
        )

        hxltm_caput_okay = False

        # Defallo (id est: non conceptum_codicem de XML)
        conceptum_numerum = 1
        conceptum_sacuum = None

        # print(self._fontem_linguam.linguam)
        # print(self._objectivum_linguam.linguam)

        # if self._ontologia.de('terminum_habendum_multum',
        #                       fontem=ontologia_de_xml) is False:
        #     self.in_formatum.definitionem_linguam(False)

        terminum_habendum_multum = self._ontologia.de(
            'terminum_habendum_multum', fontem=ontologia_de_xml)

        if terminum_habendum_multum:
            if not self._agendum_linguam:
                print("ERRŌREM: --agendum-linguam?")
                sys.exit(self.EXITUM_SYNTAXIM)

        terminum_habendum_fontem = self._ontologia.de(
            'terminum_habendum_fontem',  False, fontem=ontologia_de_xml)

        if terminum_habendum_fontem:
            if self._fontem_linguam:
                self.in_formatum.definitionem_linguam_fontem(
                    self._fontem_linguam
                )
                # HOTFIX; do code refactoring later
                # opus_fontem_linguam = self.in_formatum.fontem_linguam
            else:
                print("ERRŌREM: --fontem-linguam ?")
                sys.exit(self.EXITUM_SYNTAXIM)
                # return self.EXITUM_SYNTAXIM

        terminum_habendum_objectivum = self._ontologia.de(
            'terminum_habendum_objectivum',  False, fontem=ontologia_de_xml)

        if terminum_habendum_objectivum:
            if self._objectivum_linguam:
                self.in_formatum.definitionem_linguam_objectivum(
                    self._objectivum_linguam
                )
                # HOTFIX; do code refactoring later
                # opus_objectivum_linguam = self.in_formatum.objectivum_linguam
            else:
                print("ERRŌREM: --objectivum-linguam ?")
                sys.exit(self.EXITUM_SYNTAXIM)
                # return self.EXITUM_SYNTAXIM

        if self._ontologia.de('terminum_habendum_objectivum',
                              fontem=ontologia_de_xml) is False:
            self.in_formatum.definitionem_linguam_objectivum(False)

        III_terminum_habendum_accuratum = \
            bool(self._ontologia.de(
                'terminum_habendum_accuratum', False, fontem=ontologia_de_xml))

        if III_terminum_habendum_accuratum:
            self.in_formatum.definitionem_habendum_accuratum(True)

        III_terminum_habendum_typum = \
            bool(self._ontologia.de(
                'terminum_habendum_typum', False, fontem=ontologia_de_xml))

        if III_terminum_habendum_typum:
            # print('tem')
            self.in_formatum.definitionem_habendum_typum(True)

        # contextum: multum linguam  . . . . . . . . . . . . . . . . . . . . .
        # > Vacuum

        # contextum: linguam fontem et linguam objectīvum . . . . . . . . . .
        # > Vacuum

        # I glossarium > II conceptum --------------------------------------- #
        # Contextum: commūne ..................................................

        II_conceptum_signum = self._ontologia.de(
            'conceptum_codicem.signum', fontem=ontologia_de_xml
        )
        II_conceptum_de_attributum = self._ontologia.de(
            'conceptum_codicem.de_attributum', False, fontem=ontologia_de_xml
        )

        # I glossarium > II conceptum > III linguam ------------------------- #
        # contextum: commūne . . . . . . . . . . . . . . . . . . . . . . . . .
        # > Vacuum

        # contextum: multum linguam  . . . . . . . . . . . . . . . . . . . . .

        III_linguam_signum = self._ontologia.de(
            'linguam_codicem.signum', fontem=ontologia_de_xml
        )
        III_linguam_de_attributum = self._ontologia.de(
            'linguam_codicem.de_attributum', False, fontem=ontologia_de_xml
        )

        # contextum: linguam fontem et linguam objectīvum . . . . . . . . . . .
        # III_linguam_fontem_signum = self._ontologia.de(
        #     'linguam_fontem_codicem.signum', fontem=ontologia_de_xml
        # )
        # III_linguam_fontem_de_attributum = self._ontologia.de(
        #     'linguam_fontem_codicem.de_attributum',
        #     False, fontem=ontologia_de_xml
        # )

        # III_linguam_objectivum_signum = self._ontologia.de(
        #     'linguam_objectivum_codicem.signum', fontem=ontologia_de_xml
        # )
        # III_linguam_objectivum_de_attributum = self._ontologia.de(
        #     'linguam_objectivum_codicem.de_attributum',
        #     False, fontem=ontologia_de_xml
        # )

        # I glossarium > II conceptum > III linguam > IV terminum ----------- #
        # contextum: commūne . . . . . . . . . . . . . . . . . . . . . . . . .
        # Vacuum

        IV_terminum_accuratum = self._ontologia.de(
            'terminum_accuratum', False, fontem=ontologia_de_xml
        )

        IV_terminum_typum = self._ontologia.de(
            'terminum_typum', False, fontem=ontologia_de_xml
        )

        IV_terminum_linguam_HOTFIX = self._ontologia.de(
            'linguam_linguam', False, fontem=ontologia_de_xml
        )

        # print(IV_terminum_accuratum)

        # contextum: multum linguam  . . . . . . . . . . . . . . . . . . . . .

        IV_terminum_valorem_signum = self._ontologia.de(
            'terminum_valorem.signum', False, fontem=ontologia_de_xml
        )
        IV_terminum_valorem_de_attributum = self._ontologia.de(
            'terminum_valorem.de_attributum', False, fontem=ontologia_de_xml
        )

        # contextum: linguam fontem et linguam objectīvum . . . . . . . . . . .
        IV_terminum_fontem_valorem_signum = self._ontologia.de(
            'terminum_fontem_valorem.signum', False, fontem=ontologia_de_xml
        )
        IV_terminum_fontem_valorem_de_attributum = self._ontologia.de(
            'terminum_fontem_valorem.de_attributum', False,
            fontem=ontologia_de_xml
        )

        IV_terminum_objectivum_valorem_signum = self._ontologia.de(
            'terminum_objectivum_valorem.signum', False,
            fontem=ontologia_de_xml
        )
        IV_terminum_objectivum_valorem_de_attributum = self._ontologia.de(
            'terminum_objectivum_valorem.de_attributum', False,
            fontem=ontologia_de_xml
        )
        # print(IV_terminum_objectivum_valorem_signum)

        for eventum, nodum in self.iteratianem:

            xml_nunc_signum = HXLTMUtil.xml_clavem_breve(nodum.tag)
            xml_nunc_attributum = self._de_commune_xml_nodum_attributum(nodum)
            # print("\tnodum.tag {0} eventum {1}".format(nodum.tag, eventum))
            # contextum: multum linguam  . . . . . . . . . . . . . . . . . . .

            # Linguam codicem?
            if xml_nunc_signum == III_linguam_signum:

                if not III_linguam_de_attributum:
                    raise NotImplementedError(
                        'non III_linguam_de_attributum [{0}]'.format(
                            ontologia_de_xml))

                if eventum != 'start':
                    continue

                linguam_codicem = xml_nunc_attributum.get(
                    III_linguam_de_attributum, conceptum_numerum)

                # print('linguam_codicem', linguam_codicem)

                conceptum_sacuum = HXLTMUtil.conceptum_saccum(
                    valorem=str(xml_nunc_attributum.get(
                        III_linguam_de_attributum,
                        conceptum_numerum
                    )).strip(),
                    libellam_et_typum='linguam.codicem',
                    linguam_crudum_aut_typum=linguam_codicem,
                    saccum=conceptum_sacuum
                )

            # print('ooi', IV_terminum_linguam_HOTFIX, nodum)
            # IV_terminum_linguam_HOTFIX
            if self._de_commune_xml_nodum_est(
                    nodum, eventum, IV_terminum_linguam_HOTFIX):
                # print('trying now...')

                linguam_codicem = self._de_commune_xml_nodum_quod_valorem(
                    nodum, eventum, IV_terminum_linguam_HOTFIX)

                # conceptum_sacuum = HXLTMUtil.conceptum_saccum(
                #     valorem=self._de_commune_xml_nodum_quod_valorem(
                #         nodum, eventum, IV_terminum_linguam_HOTFIX),
                #     libellam_et_typum='terminum.accuratum',
                #     linguam_crudum=linguam_codicem,
                #     saccum=conceptum_sacuum
                # )
                conceptum_sacuum = HXLTMUtil.conceptum_saccum(
                    valorem=linguam_codicem,
                    libellam_et_typum='linguam.codicem',
                    linguam_crudum_aut_typum=linguam_codicem,
                    saccum=conceptum_sacuum
                )

            # Linguam codicem!! terminum valōrem!?
            if xml_nunc_signum == IV_terminum_valorem_signum:

                if IV_terminum_valorem_de_attributum:
                    raise NotImplementedError(
                        'non IV_terminum_valorem_de_attributum [{0}]'.format(
                            ontologia_de_xml))

                if eventum != 'end':
                    continue

                conceptum_sacuum = HXLTMUtil.conceptum_saccum(
                    valorem=str(nodum.text).strip(),
                    libellam_et_typum='terminum.valorem',
                    linguam_crudum_aut_typum=linguam_codicem,
                    saccum=conceptum_sacuum
                )

            # IV_terminum_accuratum
            if self._de_commune_xml_nodum_est(
                    nodum, eventum, IV_terminum_accuratum):
                conceptum_sacuum = HXLTMUtil.conceptum_saccum(
                    valorem=self._de_commune_xml_nodum_quod_valorem(
                        nodum, eventum, IV_terminum_accuratum),
                    libellam_et_typum='terminum.accuratum',
                    linguam_crudum_aut_typum=linguam_codicem,
                    saccum=conceptum_sacuum
                )

                # print('oooi', conceptum_sacuum)

            # IV_terminum_typum
            if self._de_commune_xml_nodum_est(
                    nodum, eventum, IV_terminum_typum):
                conceptum_sacuum = HXLTMUtil.conceptum_saccum(
                    valorem=self._de_commune_xml_nodum_quod_valorem(
                        nodum, eventum, IV_terminum_typum),
                    libellam_et_typum='terminum.typum',
                    linguam_crudum_aut_typum=linguam_codicem,
                    saccum=conceptum_sacuum
                )

                # print('oooi', conceptum_sacuum)

            # contextum: linguam fontem et linguam objectīvum . . . . . . . . .
            # if xml_nunc_signum == III_linguam_fontem_signum:

            #     if III_terminum_habendum_accuratum:
            #         raise NotImplementedError(
            #             'non III_terminum_habendum_accuratum [{0}]'.format(
            #                 ontologia_de_xml))

            #     if not III_linguam_fontem_de_attributum:
            #         raise NotImplementedError(
            #             'non III_linguam_fontem_de_attributum [{0}]'.format(
            #                 ontologia_de_xml))

            #     if eventum != 'start':
            #         continue

            #     linguam_fontem_codicem = xml_nunc_attributum.get(
            #         III_linguam_fontem_de_attributum,
            #         self._fontem_linguam.linguam)
            #     # linguam_fontem_codicem = self._fontem_linguam.linguam

            #     # if not linguam_fontem_codicem:
            #     #     linguam_fontem_codicem = self._fontem_linguam.linguam

            #     # Hotfix XLIFF with country codes
            #     # TODO: generalize it later
            #     if isinstance(linguam_fontem_codicem, str) and \
            #             len(linguam_fontem_codicem) == 5 and \
            #             linguam_fontem_codicem.find('-') == 2:
            #         linguam_fontem_codicem = \
            #             linguam_fontem_codicem.split('-')[0]

            #     conceptum_sacuum = HXLTMUtil.conceptum_saccum(
            #         valorem=str(xml_nunc_attributum.get(
            #             III_linguam_fontem_de_attributum,
            #             # conceptum_numerum
            #             linguam_fontem_codicem
            #         )).strip(),
            #         libellam_et_typum='linguam.fontem_codicem',
            #         linguam_crudum=linguam_fontem_codicem,
            #         saccum=conceptum_sacuum
            #     )

            if xml_nunc_signum == IV_terminum_fontem_valorem_signum:

                if IV_terminum_fontem_valorem_de_attributum:
                    raise NotImplementedError(
                        'non IV_terminum_fontem_valorem_de_attributum [{0}]'.
                        format(ontologia_de_xml))

                conceptum_sacuum = HXLTMUtil.conceptum_saccum(
                    valorem=str(nodum.text).strip(),
                    libellam_et_typum='terminum.valorem',
                    linguam_crudum_aut_typum='fontem',
                    # linguam_crudum_aut_typum=opus_fontem_linguam.linguam,
                    saccum=conceptum_sacuum
                )

            # if xml_nunc_signum == III_linguam_objectivum_signum:

            #     if III_terminum_habendum_accuratum:
            #         raise NotImplementedError(
            #             'non III_terminum_habendum_accuratum [{0}]'.format(
            #                 ontologia_de_xml))

            #     if not III_linguam_objectivum_de_attributum:
            #         raise NotImplementedError(
            #             'non III_linguam_objectivum_de_attributum [{0}]'.
            #             format(ontologia_de_xml))

            #     if eventum != 'start':
            #         continue

            #     # linguam_objectivum_codicem = xml_nunc_attributum.get(
            #     #     III_linguam_objectivum_de_attributum,
            #           conceptum_numerum)
            #     linguam_objectivum_codicem = xml_nunc_attributum.get(
            #         III_linguam_objectivum_de_attributum,
            #         self._objectivum_linguam.linguam)

            #     # linguam_objectivum_codicem = \
            #     #     self._objectivum_linguam.linguam

            #     # Hotfix XLIFF with country codes
            #     # TODO: generalize it later
            #     if isinstance(linguam_objectivum_codicem, str) and \
            #             len(linguam_objectivum_codicem) == 5 and \
            #             linguam_objectivum_codicem.find('-') == 2:
            #         linguam_objectivum_codicem = \
            #             linguam_objectivum_codicem.split('-')[0]

            #     # print(linguam_objectivum_codicem)

            #     conceptum_sacuum = HXLTMUtil.conceptum_saccum(
            #         valorem=str(xml_nunc_attributum.get(
            #             III_linguam_objectivum_de_attributum,
            #             linguam_objectivum_codicem
            #         )).strip(),
            #         libellam_et_typum='linguam.objectivum_codicem',
            #         linguam_crudum=linguam_objectivum_codicem,
            #         saccum=conceptum_sacuum
            #     )

            if xml_nunc_signum == IV_terminum_objectivum_valorem_signum:

                if IV_terminum_objectivum_valorem_de_attributum:
                    raise NotImplementedError(
                        'non IV_terminum_objectivum_valorem_de_attributum'
                        ' [{0}]'.format(ontologia_de_xml))

                conceptum_sacuum = HXLTMUtil.conceptum_saccum(
                    valorem=str(nodum.text).strip(),
                    libellam_et_typum='terminum.valorem',
                    linguam_crudum_aut_typum='objectivum',
                    # linguam_crudum_aut_typum=opus_objectivum_linguam.linguam,
                    saccum=conceptum_sacuum
                )

            # contextum: commūne . . . . . . . . . . . . . . . . . . . . . . .

            if xml_nunc_signum == II_conceptum_signum:

                if eventum != 'end':
                    continue

                if not II_conceptum_de_attributum:
                    raise NotImplementedError(
                        'non II_conceptum_de_attributum [{0}]'.format(
                            ontologia_de_xml))

                # conceptum_codicem = xml_nunc_attributum.get(
                #     codicem_de_attributum, conceptum_numerum)

                conceptum_sacuum = HXLTMUtil.conceptum_saccum(
                    valorem=str(xml_nunc_attributum.get(
                        II_conceptum_de_attributum,
                        conceptum_numerum)).strip(),
                    libellam_et_typum='conceptum.codicem',
                    saccum=conceptum_sacuum
                )

                # if conceptum_attributum in xml_nunc_attributum:
                #     conceptum_codicem = \
                #         xml_nunc_attributum[conceptum_attributum]

                if not hxltm_caput_okay:
                    resultatum_csv.writerow(
                        self.in_formatum.in_caput())
                    hxltm_caput_okay = True

                lineam = self.in_formatum.in_lineam_de_conceptum_sacuum(
                    conceptum_sacuum)

                # print('')
                # print('')
                # print('conceptum_sacuum', conceptum_sacuum)
                # print('')
                # print('')

                conceptum_sacuum = None

                for crudum_lineam in lineam:
                    resultatum_csv.writerow(crudum_lineam)

                conceptum_numerum += 1

                conceptum_sacuum = None
                nodum.clear()

        return self.EXITUM_CORRECTUM

    def _de_commune_xml_nodum_attributum(
            self, nodum) -> Dict:  # pylint: disable=no-self-use
        """_de_commune_xml_nodum_attributum

        Args:
            nodum ([xml.etree.ElementTree ]):

        Returns:
            Dict:
        """
        # pylint: disable=no-self-use
        xml_attributum_nunc = {}

        if hasattr(nodum, 'attrib'):
            for clavem in list(nodum.attrib):
                clavem_basim = HXLTMUtil.xml_clavem_breve(clavem)
                xml_attributum_nunc[clavem] = nodum.attrib[clavem]

                if clavem_basim != clavem and \
                        clavem_basim not in nodum.attrib:
                    xml_attributum_nunc[clavem_basim] = \
                        nodum.attrib[clavem]

        return xml_attributum_nunc

    def _de_commune_xml_nodum_est(
            self,
            nodum,
            eventum,
            referens: Dict = None
    ) -> Dict:
        """_de_commune_xml_nodum_est

        _[eng-Latn]
        Compare the XML node with the *.hxltm.yml option. Return true
        if this node at this very own event could return the expected
        value
        [eng-Latn]_

        Args:
            nodum ([xml.etree.ElementTree]):
            nodum (str): Nodum XML eventum
            referens (Dict): *.hxltm.yml optionem

        Returns:
            Dict:
        """
        # print('_de_commune_xml_nodum_est', nodum, referens)
        if not referens or not isinstance(referens, dict):
            return False

        if 'de_signum' in referens and nodum.tag != referens['de_signum']:
            return False

        nodum_attbs = self._de_commune_xml_nodum_attributum(nodum)

        if 'de_attributum' in referens and bool(referens['de_attributum']):
            clavem = referens['de_attributum'].keys()
            for item in clavem:
                if item not in nodum_attbs or \
                        referens['de_attributum'][item] != nodum_attbs[item]:
                    return False

        if referens['ad'] == 'XML-nodum-textum' and eventum != 'end':
            return False

        if referens['ad'] == 'XML-nodum-attributum' and eventum != 'start':
            # print('yay')
            return False

        # print('>foi <')

        return True

    def _de_commune_xml_nodum_quod_valorem(
            self,
            nodum,
            _eventum,
            referens: Dict = None
    ) -> Dict:
        """_de_commune_xml_nodum_quod_valorem

        _[eng-Latn]
        Return the value.
        [eng-Latn]_

        Args:
            nodum ([xml.etree.ElementTree]):
            _eventum (str): Nodum XML eventum
            referens (Dict): *.hxltm.yml optionem

        Returns:
            Dict:
        """
        if not referens or not isinstance(referens, dict):
            # return False
            raise SyntaxError('referens?')

        in_praefixum = referens['in_praefixum'] \
            if 'in_praefixum' in referens else ''
        in_suffixum = referens['in_suffixum'] \
            if 'in_suffixum' in referens else ''

        nodum_attbs = self._de_commune_xml_nodum_attributum(nodum)

        if referens['ad'] == 'XML-nodum-textum':
            return in_praefixum + str(nodum.text).strip() + in_suffixum

        if referens['ad'].startswith('XML-nodum-attributum'):
            _, xml_attr = referens['ad'].split(':')
            # print(xml_attr, nodum_attbs, nodum, referens)
            return (in_praefixum + str(nodum_attbs[xml_attr]).strip()
                    + in_suffixum)

        raise ValueError('Nodum {0} referens {1}'.format(nodum, referens))

    def de_tbx(self):
        """de_tbx [summary]

        [extended_summary]

        Returns:
            [type]: [description]
        """

        if self.radicem_signum == 'martif':
            ontologia_de_xml = \
                self._ontologia.crudum['normam']['TBX-Basim']['de_xml']
        if self.radicem_signum == 'tbx':
            ontologia_de_xml = \
                self._ontologia.crudum['normam']['TBX-2019']['de_xml']

        return self._de_commune_xml(ontologia_de_xml)

    def de_xml(self):

        ontologia_de_xml = \
            self._ontologia.crudum['normam']['XML']['de_xml']

        return self._de_commune_xml(ontologia_de_xml)
        # raise NotImplementedError('XML {0}'.format(str(self.xml_typum)))

    def de_tmx(self):
        """de_tmx De Translation Memory eXchange (TMX)

        Trivia:
            - Normam: https://www.gala-global.org/tmx-14b
            - DTD: https://www.gala-global.org/sites/default
                   /files/migrated-pages/docs/tmx14%20%281%29.dtd
        Returns:
            [int]:
        """

        ontologia_de_xml = \
            self._ontologia.crudum['normam']['TMX']['de_xml']

        return self._de_commune_xml(ontologia_de_xml)

    def de_xliff(self):
        """de_xliff
        """

        ontologia_de_xml = \
            self._ontologia.crudum['normam']['XLIFF']['de_xml']

        return self._de_commune_xml(ontologia_de_xml)

    def de_xliff_obsoletum(self):
        """de_xliff_obsoletum
        """
        ontologia_de_xml = \
            self._ontologia.crudum['normam']['XLIFF-obsoletum']['de_xml']

        return self._de_commune_xml(ontologia_de_xml)

    def quod_archivum_typum(self):
        """quod_archivum_typum [summary]

        Trivia:
        - quod, https://en.wiktionary.org/wiki/qui#Latin
        - archīvum, https://en.wiktionary.org/wiki/archivum
        - typum, https://en.wiktionary.org/wiki/typus#Latin

        Returns:
            [str]: archīvum typum
        """
        # pylint: disable=no-self-use
        resultatum = 'xml'
        # todo: implement other checks
        return resultatum

    # def quod_archivum_xml_basim(self) -> Dict:
    #     resultatum = {}

    #     # print(self.arborem_radicem)
    #     # print(self.arborem_radicem.tag)
    #     # print(self.arborem_radicem.attrib)

    #     print(self._ontologia.quod_xml_typum(
    #         self.arborem_radicem.tag,
    #         self.arborem_radicem.attrib
    #     ))
    #     return resultatum

    def in_archivum(self):
        """in_archivum archīvum fontem in archīvum objectīvum

        Returns:
            [int]: EXITUM_CORRECTUM, EXITUM_ERROREM aut EEXITUM_SYNTAXIM
        """
        return self.in_archivum_formatum_hxltm()

    def in_archivum_formatum_hxltm(self):
        """in_archivum archīvum fontem in archīvum objectīvum fōrmātum HXLTM

        Returns:
            [int]: EXITUM_CORRECTUM, EXITUM_ERROREM aut EXITUM_SYNTAXIM
        """
        # self.quod_archivum_xml_basim()
        # print("self.xml_typum\t\t", self.xml_typum)
        if self.xml_typum and 'hxltm_normam' in self.xml_typum:
            if self.xml_typum['hxltm_normam'].startswith('TBX'):
                return self.de_tbx()
            if self.xml_typum['hxltm_normam'].startswith('TMX'):
                return self.de_tmx()
            if self.xml_typum['hxltm_normam'].startswith('XLIFF'):
                if self.xml_typum['hxltm_normam'].startswith(
                        'XLIFF-obsoletum'):
                    return self.de_xliff_obsoletum()
                else:
                    return self.de_xliff()

            # if self.xml_typum['typum'] == 'XML':
            #     return self.de_xml()

            return self.de_xml()
        # self.testum()

        return self.EXITUM_ERROREM

#     def testum(self):

#         tree = XMLElementTree.parse(self.fontem_archivum)
#         # tree = ET.parse(self.archivum)
#         root = tree.getroot()

#         # print(root.tag)

#         self.xliff_obsoletum(root)
#         self.xliff_testum2()

#     def xliff_obsoletum(self, root):
#         print('oi')

#         print(root.findall('./{*}file/{*}body/{*}trans-unit'))
#         print('')

#     def xliff_testum2(self):
#         """xliff_testum2
#         """
#         # pylint: disable=no-self-use
#         # @see https://docs.python.org/3/library
#         #      /xml.etree.elementtree.html#elementtree-xpath
#         crudum = """<?xml version="1.0"?>
# <actors xmlns:fictional="http://characters.example.com"
#         xmlns="http://people.example.com">
#     <actor>
#         <name>John Cleese</name>
#         <fictional:character>Lancelot</fictional:character>
#         <fictional:character>Archie Leach</fictional:character>
#     </actor>
#     <actor>
#         <name>Eric Idle</name>
#         <fictional:character>Sir Robin</fictional:character>
#         <fictional:character>Gunther</fictional:character>
#         <fictional:character>Commander Clement</fictional:character>
#     </actor>
# </actors>
#         """

#         root = XMLElementTree.fromstring(crudum)

#         print(root.findall("."))

#         print(root.findall("./country/neighbor"))


@dataclass
class HXLTMLinguam:  # pylint: disable=too-many-instance-attributes
    """HXLTM linguam auxilium programmi

    Exemplōrum gratiā (et Python doctest, id est, testum automata):

>>> HXLTMLinguam('lat-Latn@la-IT@IT')
HXLTMLinguam()

>>> HXLTMLinguam('lat-Latn@la-IT@IT').v()
{'_typum': 'HXLTMLinguam', \
'crudum': 'lat-Latn@la-IT@IT', 'linguam': 'lat-Latn', \
'bcp47': 'la-IT', 'imperium': 'IT', 'iso6391a2': 'la', 'iso6393': 'lat', \
'iso115924': 'Latn'}

>>> HXLTMLinguam('lat-Latn@la-IT@IT', meta={'testum': 123}).v()
{'_typum': 'HXLTMLinguam', '_vanandum_insectum_meta': {'testum': 123}, \
'crudum': 'lat-Latn@la-IT@IT', 'linguam': 'lat-Latn', 'bcp47': 'la-IT', \
'imperium': 'IT', 'iso6391a2': 'la', 'iso6393': 'lat', 'iso115924': 'Latn'}

>>> HXLTMLinguam('lat-Latn@la-IT@IT').a()
'+i_la+i_lat+is_latn+ii_it'

        Kalo Finnish Romani, Latin script (no ISO 2 language)

>>> HXLTMLinguam('rmf-Latn').v()
{'_typum': 'HXLTMLinguam', 'crudum': 'rmf-Latn', \
'linguam': 'rmf-Latn', 'iso6393': 'rmf', 'iso115924': 'Latn', 'bcp47': 'rmf'}

        Kalo Finnish Romani, Latin script (no ISO 2 language, so no attr)

>>> HXLTMLinguam('rmf-Latn').a()
'+i_rmf+is_latn'

        Private use language tags: se use similar pattern of BCP 47.
        (https://tools.ietf.org/search/bcp47)

>>> HXLTMLinguam('lat-Latn-x-privatum').a()
'+i_lat+is_latn+ix_privatum'

>>> HXLTMLinguam('lat-Latn-x-privatum-tag8digt').a()
'+i_lat+is_latn+ix_privatum+ix_tag8digt'

        If x-private is only on BCP, we ignore it on HXL attrs.
        Tools may still use this for other processing (like for XLIFF),
        but not for generated Datasets.

>>> HXLTMLinguam(
... 'cmn-Latn@zh-Latn-CN-variant1-a-extend1-x-wadegile-private1').a()
'+i_zh+i_cmn+is_latn'

        To force a x-private language tag, it must be on linguam (first part)
        even if it means repeat. Also, we create attributes shorted by
        ASCII alphabet, as BCP47 would do

>>> HXLTMLinguam(
... 'cmn-Latn-x-wadegile-private1@zh-CN-x-wadegile-private1').a()
'+i_zh+i_cmn+is_latn+ix_private1+ix_wadegile'


>>> HXLTMLinguam(
... 'lat-Latn-x-caesar12-romanum1@la-IT-x-caesar12-romanum1@IT').a()
'+i_la+i_lat+is_latn+ii_it+ix_caesar12+ix_romanum1'

    """

    # Exemplum: lat-Latn@la-IT@IT, arb-Arab@ar-EG@EG
    _typum: InitVar[str] = None  # 'HXLTMLinguam'
    _vanandum_insectum_meta: InitVar[Dict] = None
    crudum: InitVar[str] = None
    linguam: InitVar[str] = None     # Exemplum: lat-Latn, arb-Arab
    bcp47: InitVar[str] = None       # Exemplum: la-IT, ar-EG
    imperium: InitVar[str] = None    # Exemplum: IT, EG
    iso6391a2: InitVar[str] = None     # Exemlum: la, ar
    iso6393: InitVar[str] = None     # Exemlum: lat, arb
    iso115924: InitVar[str] = None   # Exemplum: Latn, Arab
    privatum: InitVar[List[str]] = None  # Exemplum: [privatum]
    vacuum: InitVar[str] = False

    # https://tools.ietf.org/search/bcp47#page-2-12

    # def __init__(self, linguam: str, strictum=False, vacuum=False):
    def __init__(self, linguam: str,
                 strictum=False, vacuum=False, meta=None):
        """HXLTMLinguam initiāle

        Args:
            linguam (str): Textum linguam
            strictum (bool, optional): Strictum est?.
                       Trivia: https://en.wiktionary.org/wiki/strictus#Latin
                       Defallo falsum.
            vacuum (bool, optional): vacuum	est?
                       Trivia: https://en.wiktionary.org/wiki/vacuus#Latin.
                       Defallo falsum.
            meta (Dict, optional):
                    Metadatum ad Vēnandum īnsectum.Defallo vacuum.
        """
        # super().__init__()
        self._typum = 'HXLTMLinguam'  # Used only when output JSON
        if meta is not None:
            self._vanandum_insectum_meta = meta
        self.crudum = linguam
        if not vacuum:
            self.initialle(strictum)
        else:
            self.vacuum = vacuum

    def initialle(self, strictum: bool):  # pylint: disable=too-many-branches
        """
        Trivia: initiāle, https://en.wiktionary.org/wiki/initialis#Latin
        """

        term = self.crudum
        # Hackysh way to discover if private use is the linguam
        # tag or if is the BCP47 x-private use tag
        # Good example '4.4.2.  Truncation of Language Tags'
        # at https://tools.ietf.org/search/bcp47
        if self.crudum.find('x-') > -1:
            # print('Do exist a private-use tag')
            if self.crudum.find('@') > -1:
                parts = self.crudum.split('@')
                # print('parte1', parts)
                if parts[0].find('x-') > -1:
                    # _, privatumtext = parts[0].split('-x-')
                    part0, privatumtext = parts[0].split('-x-')
                    self.privatum = privatumtext.split('-')
                    parts.pop(0)
                    term = part0 + "@" + '@'.join(parts)
                    # print('term2', term)
                    # TODO: handle private use on linguan tag when
                    #       also BCP47 is used
            else:
                part0, privatumtext = self.crudum.split('-x-')
                self.privatum = privatumtext.split('-')
                term = part0

        if term.find('@') == -1:
            # Non @? Est linguam.
            self.linguam = term

            # self.iso6393, self.iso115924 = \
            #     list(self.linguam.split('-'))
        elif term.find('@@') > -1:
            # @@? Est linguam et imperium
            self.linguam, self.imperium = list(term.split('@@'))

            # self.iso6393, self.iso115924 = \
            #     list(self.linguam.split('-'))
        elif term.count('@') == 1:
            # Unum @? Est linguam et bcp47
            self.linguam, self.bcp47 = list(term.split('@'))

        elif term.count('@') == 2:
            # rem@rem@rem ? Est linguam, bcp47, imperium
            self.linguam, self.bcp47, self.imperium = \
                list(term.split('@'))
            # self.iso6393, self.iso115924 = \
            #     list(self.linguam.split('-'))
        elif strictum:
            raise ValueError('HXLTMLinguam [' + term + ']')
        else:
            return False

        if self.bcp47:
            parts = self.bcp47.split('-')
            if len(parts[0]) == 2:
                self.iso6391a2 = parts[0].lower()

        self.iso6393, self.iso115924 = \
            list(self.linguam.split('-'))

        self.iso6393 = self.iso6393.lower()
        self.iso115924 = self.iso115924.capitalize()
        self.linguam = self.iso6393 + '-' + self.iso115924
        if self.imperium:
            self.imperium = self.imperium.upper()

        # Tags like ancient greek, grc-Grek, should still have BCP47
        if not self.bcp47 and self.iso6393:
            self.bcp47 = self.iso6393

        if self.privatum is not None and len(self.privatum) > 0:
            # https://tools.ietf.org/search/bcp47#page-2-12
            # '4.5.  Canonicalization of Language Tags'
            # We short the keys
            # privatum_est = sorted(self.imperium, key=str.upper)

            # print('antes', self.imperium)
            privatum_est = sorted(self.privatum)

            # print('depois', self.privatum)
            self.privatum = privatum_est

        return True

    def a(self):  # pylint: disable=invalid-name
        """HXL attribūtum

        Exemplum:
            >>> HXLTMLinguam('lat-Latn@la-IT@IT').a()
            '+i_la+i_lat+is_latn+ii_it'

        Returns:
            [str]: textum HXL attribūtum
        """
        resultatum = []

        if self.iso6391a2:
            resultatum.append('+i_' + self.iso6391a2)
        if self.iso6393:
            resultatum.append('+i_' + self.iso6393)
        if self.iso115924:
            resultatum.append('+is_' + self.iso115924)
        if self.imperium:
            resultatum.append('+ii_' + self.imperium)
        if self.privatum and len(self.privatum) > 0:
            for item in self.privatum:
                resultatum.append('+ix_' + item)

        return ''.join(resultatum).lower()

    def aequale(
            self,
            clavem_et_linguam: Union[str, Type['HXLTMLinguam']]) -> int:
        """aequāle crudum clavem?

        Args:
            clavem_et_linguam (str, HXLTMLinguam): Textum crudum et linguam

        Returns:
            int: aequāle numerum
        """
        # @TODO: the numeric results on this function are still an usable
        #        draft. They can be used later to assert the closest
        #        option to return a viable result

        if clavem_et_linguam and isinstance(clavem_et_linguam, str):
            neo = HXLTMLinguam(clavem_et_linguam)
        else:
            neo = clavem_et_linguam

        # print(neo.a(), self.a())

        if neo.a() == self.a():
            return 100

        if neo.iso6391a2 == self.iso6391a2 and \
                neo.iso6393 == self.iso6393 and \
                neo.iso115924 == self.iso115924 and \
                neo.imperium == self.imperium:
            # non privatum
            return 95

        if neo.iso6391a2 == self.iso6391a2 and \
                neo.iso6393 == self.iso6393 and \
                neo.iso115924 == self.iso115924 and \
                neo.privatum == self.privatum:
            # non imperium
            return 95

        if neo.iso6393 == self.iso6393 and \
                neo.iso115924 == self.iso115924 and \
                (neo.privatum == self.privatum or
                    neo.privatum == self.privatum):
            # non iso6391a2
            # non imperium || non privatum
            return 95

        if neo.iso6393 == self.iso6393 and \
                neo.iso115924 == self.iso115924:
            # non iso6391a2
            # non privatum
            # non imperium
            return 90

        return -100

    def designo(self, clavem: str, rem: Any) -> Type['HXLTMLinguam']:
        """Designo clavem rem

        _[eng-Latn] The HXLTMLinguam.designo() can be useful for create empty
                    languages with HXLTMLinguam('', vacuum=True) and then
                    manually defining what attributes would like when search
                    by hashtags
        [eng-Latn]_

       Args:
            clavem (str): clāvem, https://en.wiktionary.org/wiki/clavis#Latin
            rem (Any): rem, https://en.wiktionary.org/wiki/res#Latin

        Returns:
            [HXLTMLinguam]: HXLTMLinguam to allow method chaining

        Exemplum:
>>> rem_vacuum = HXLTMLinguam('', vacuum=True)
>>> rem = rem_vacuum.designo('iso115924', 'Latn')
>>> collectionem = [
...    '#item+conceptum+codicem',
...    '#item+rem+i_la+i_lat+is_latn',
...    '#item+definitionem+i_la+i_lat+is_latn',
...    '#item+rem+i_ar+i_arb+is_arab',
...    '#item+definitionem+i_ar+i_arb+is_arab'
... ]
>>> rem.intra_collectionem_est(collectionem)
['#item+rem+i_la+i_lat+is_latn', '#item+definitionem+i_la+i_lat+is_latn']


        """
        setattr(self, clavem, rem)
        return self

    def h(self, formatum: str):  # pylint: disable=invalid-name
        """HXL hashtag de fōrmātum

        Exemplum:
>>> HXLTMLinguam('lat-Latn@la-IT@IT').h('#item+rem__linguam__')
'#item+rem+i_la+i_lat+is_latn+ii_it'

>>> HXLTMLinguam('lat-Latn-x-privatum').h('#item+rem__linguam__')
'#item+rem+i_lat+is_latn+ix_privatum'

        Returns:
            [str]: textum HXL hashtag
        """
        linguam_attrs = self.a()

        if formatum.find('__linguam__') > -1:
            return formatum.replace('__linguam__', linguam_attrs)

        if formatum.find('__linguam_de_imperium__') > -1:
            return formatum.replace('__linguam_de_imperium__', linguam_attrs)

        raise ValueError('HXLTMLinguam fōrmātum errōrem [' + formatum + ']')

    def intra_collectionem_est(
            self, collectionem: List, formatum: str = None) -> List:
        """Intrā collēctiōnem est?

        Trivia:
        - intrā, https://en.wiktionary.org/wiki/intra#Latin
        - collēctiōnem, https://en.wiktionary.org/wiki/collectio#Latin
        - est, https://en.wiktionary.org/wiki/est#Latin


        Args:
            collectionem (List): List of HXL hashtags
            formatum (str): An formatted template.

        Returns:
            [List]: List of HXL hashtags that match the search

        Tests:

>>> rem = HXLTMLinguam('lat-Latn@la')
>>> collectionem = [
...    '#item+conceptum+codicem',
...    '#item+rem+i_la+i_lat+is_latn',
...    '#item+definitionem+i_la+i_lat+is_latn',
...    '#item+rem+i_ar+i_arb+is_arab',
...    '#item+definitionem+i_ar+i_arb+is_arab'
... ]

>>> rem.intra_collectionem_est(collectionem)
['#item+rem+i_la+i_lat+is_latn', '#item+definitionem+i_la+i_lat+is_latn']

>>> rem.intra_collectionem_est(collectionem, '#item+rem__linguam__')
['#item+rem+i_la+i_lat+is_latn']
>>> rem.intra_collectionem_est(collectionem,'#status+rem+accuratum__linguam__')
[]

>>> rem_vacuum = HXLTMLinguam('', vacuum=True)
>>> rem_vacuum.intra_collectionem_est(collectionem)
['#item+conceptum+codicem', \
'#item+rem+i_la+i_lat+is_latn', \
'#item+definitionem+i_la+i_lat+is_latn', \
'#item+rem+i_ar+i_arb+is_arab', \
'#item+definitionem+i_ar+i_arb+is_arab']

>>> rem_vacuum.intra_collectionem_est(collectionem, '#item+rem__linguam__')
['#item+rem+i_la+i_lat+is_latn', '#item+rem+i_ar+i_arb+is_arab']

        """
        resultatum = []
        if formatum:
            indaginem = self.h(formatum)
        else:
            indaginem = self.a()

        for rem in collectionem:
            if rem.find(indaginem) > -1:
                resultatum.append(rem)

        return resultatum

    def v(self, _verbosum: bool = None):  # pylint: disable=invalid-name
        """Ego python Dict

        Trivia:
         - valōrem, https://en.wiktionary.org/wiki/valor#Latin
         - verbosum, https://en.wiktionary.org/wiki/verbosus#Latin

        Args:
            _verbosum (bool): Verbosum est? Defallo falsum.

        Returns:
            [Dict]: Python objectīvum
        """
        return self.__dict__


class HXLTMOntologia:
    """HXLTM Ontologia

    Trivia:
        - HXLTM:
        - HXLTM, https://hdp.etica.ai/hxltm
            - HXL, https://hxlstandard.org/
            - TM, https://www.wikidata.org/wiki/Q333761
        - Ontologia
            - https://www.wikidata.org/wiki/Q44325
            - https://la.wikipedia.org/wiki/Ontologia
            - Jacob Lorhard (1561-1609): The Creator of the Term "Ontologia"
                - https://www.ontology.co/jacob-lorhard.htm

    Exemplōrum gratiā (et Python doctest, id est, testum automata):

>>> ontologia = HXLTMTestumAuxilium.ontologia()
>>> 'HXLTM' in list(ontologia.de('normam').keys())
True

>>> 'genus_grammaticum' in list(ontologia.de('ontologia_aliud').keys())
True

>>> 'partem_orationis' in list(ontologia.de('ontologia_aliud').keys())
True

>>> ontologia.quid_est_hashtag_circa_conceptum('#item+conceptum+codicem')
True

>>> ontologia.quid_est_hashtag_circa_conceptum('#rem+rem+i_la+i_lat+is_latn')
False

>>> ontologia.quid_est_hashtag_circa_linguam_aut_terminum(
...    '#item+conceptum+codicem')
False

>>> ontologia.quid_est_hashtag_circa_linguam_aut_terminum(
...    '#rem+rem+i_la+i_lat+is_latn')
True


#>>> ontologia.quod_rem_statum()
{'accuratum': None, 'crudum': [], 'crudum_originale': [], \
'XLIFF': 'initial', 'UTX': 'provisional'}


#>>> ontologia.quod_rem_statum(10, 'lat_rem_finale')
{'accuratum': 10, 'crudum': [], 'crudum_originale': ['lat_rem_finale'], \
'XLIFF': 'initial', 'UTX': 'provisional'}
#>>> ontologia.\
    quod_rem_statum(10, 'lat_rem_finale|UTX_provisional|XLIFF_initial')
{'accuratum': 10, 'crudum': [], 'crudum_originale': \
['lat_rem_finale', 'UTX_provisional', 'XLIFF_initial'], \
'XLIFF': 'initial', 'UTX': 'provisional'}


    """

    def __init__(self, ontologia: Dict, vacuum: bool = False):
        """
        _[eng-Latn] Constructs all the necessary attributes for the
                    HXLTMOntologia object.
        [eng-Latn]_
        """
        if vacuum:
            self.crudum = {}
        else:
            self.crudum = ontologia

    def hxl_de_aliud_nomen_breve(self, structum=False):
        """HXL attribūtum de aliud nōmen breve (cor.hxltm.215.yml)

        Trivia:
        - aliud, https://en.wiktionary.org/wiki/alius#Latin
        - nōmen, https://en.wiktionary.org/wiki/nomen#Latin
        - breve, https://en.wiktionary.org/wiki/brevis

        _[eng-Latn] For each item that have both __nomen_breve and __HXL,
                    create a flatten dictionary (only a key and value)
                    with the equivalent HXL hashtags.

                    This approach allows pass much more control logic to the
                    YAML file.
        [eng-Latn]_

        Returns:
            [Dict]: Dictionary
        """
        resultatum = {}
        # pylint: disable=invalid-name

        def recursionem(rem):
            # Trivia:
            # - recursiōnem, https://en.wiktionary.org/wiki/recursio#Latin
            for _k, v in rem.items():
                if isinstance(v, dict):
                    recursionem(v)
                else:
                    if '__HXL' in rem and '__nomen_breve' in rem:

                        if structum and rem['__nomen_breve'] in resultatum:
                            # TODO: improve this message
                            print('K [' + rem['__nomen_breve'] + ']')

                        resultatum[rem['__nomen_breve']] = \
                            ''.join(rem['__HXL'].split())

        # print(self.crudum)
        recursionem(self.crudum['ontologia'])
        # print(resultatum)
        return resultatum

    def hxlhashtag(self, objectivum: Union[Dict, None], strictum=False):
        """Get __HXL non-whitespace value from an Dict

        Args:
            objectivum ([Dict]): an object with __HXL
            strictum (bool, optional): Raise error?. Defaults to False.

        Raises:
            RuntimeError: [description]

        Returns:
            [str]: an HXL hashtag without spaces
        """
        # pylint: disable=no-self-use
        if objectivum is not None:
            if '__HXL' in objectivum:
                return ''.join(objectivum['__HXL'].split())

        if strictum:
            raise RuntimeError('HXLTMOntologia.hxlhashtag error')
        return None

    def de(self, dotted_key: str,  # pylint: disable=invalid-name
           default: Any = None, fontem: dict = None) -> Any:
        """
        Trivia: dē, https://en.wiktionary.org/wiki/de#Latin

        Examples:
            >>> exemplum = {'a': {'a2': 123}, 'b': 456}
            >>> otlg = HXLTMOntologia(exemplum)
            >>> otlg.de('a.a2', fontem=exemplum)
            123

        Args:
            dotted_key (str): Dotted key notation
            default ([Any], optional): Value if not found. Defaults to None.
            fontem (dict): An nested object to search

        Returns:
            [Any]: Return the result. Defaults to default
        """
        if fontem is None:
            fontem = self.crudum

        keys = dotted_key.split('.')
        return reduce(
            lambda d, key: d.get(
                key) if d else default, keys, fontem
        )

    def quod_aliud(self, aliud_typum: str, aliud_valorem: str) -> Dict:
        """Quod Aliud?

        Requīsītum:
            - *.hxmtm.yml:ontologia_aliud
            - *.hxmtm.yml:ontologia_aliud_familiam

        Args:
            aliud_typum (str):
                aliud valōrem
            aliud_valōrem (str):
                aliud valōrem

        Returns:
            Dict: Python Dict, de *.hxltm.yml

    Exemplōrum gratiā (et Python doctest, id est, testum automata):

>>> ontologia = HXLTMTestumAuxilium.ontologia()
>>> 'UTX_adverb' in ontologia.\
    quod_aliud('partem_orationis', 'lat_adverbium')['aliud']
True

>>> ontologia.\
    quod_aliud('partem_orationis', 'lat_adverbium')['codicem_TBX']
'adverb'
        """
        if aliud_typum not in self.crudum['ontologia_aliud'] or \
                aliud_valorem not in \
                self.crudum['ontologia_aliud'][aliud_typum]:
            return None
        resultatum = self.crudum['ontologia_aliud'][aliud_typum][aliud_valorem]

        if '_aliud' in resultatum and resultatum['_aliud']:
            resultatum['aliud'] = \
                list(map(str.strip, resultatum['_aliud'].split('|')))
        else:
            # _[eng-Latn]Alias without aliases to other types?[eng-Latn]_
            resultatum['aliud'] = []

        aliud_familiam = self.crudum['ontologia_aliud_familiam'].keys()
        # print('aliud_familiam', aliud_familiam)
        for familiam in aliud_familiam:
            if aliud_valorem.startswith(familiam + '_'):
                resultatum['_aliud_familiam'] = familiam

            for aliud in resultatum['aliud']:
                # _[eng-Latn]
                # Only create a codicem_TTTT if *.hxmtl.yml already not have
                # one.
                # [eng-Latn]_

                if aliud.startswith(familiam + '_') and \
                        not 'codicem_' + familiam in resultatum:
                    resultatum['codicem_' + familiam] = \
                        aliud.replace(familiam + '_', '')

        # print('   > quod_aliud resultatum', resultatum)
        return resultatum

    def quod_aliud_de_multiplum(
        self,
        aliud_typum: str,
        aliud_valorem_multiplum: Union[List[str], str]
    ) -> Dict:
        """Quod Aliud de multiplum optiōnem?

        _[eng-Latn]
        HXLTM (when not working with RAW JSON) allows make simpler short
        aliases from multiple standards, like:
            'UTX_properNoun | TBX_noun'
        In such way that it actually allows to make inferences about other
        types implicitly even when some things are obvious
        (like a 'proper noun' must be a 'noun').

        When a field alredy not explicitly define an exact value, we
        'try smart inferences', but if the initial input do already have
        something wrong (but more specific for an output format) this
        method will not override the more explicity alias.

        Advanced checks (like bad tagging) should be done in another step.
        [eng-Latn]_

        Requīsītum:
            - *.hxmtm.yml:ontologia_aliud
            - *.hxmtm.yml:ontologia_aliud_familiam

        Args:
            aliud_typum (str):
                aliud valōrem
            aliud_valorem_multiplum (Union(List[str], str)):
                aliud valōrem

        Returns:
            Dict: Python Dict, de *.hxltm.yml

        Exemplōrum gratiā (et Python doctest, id est, testum automata):

>>> ontologia = HXLTMTestumAuxilium.ontologia()

>>> testum_I = ontologia.quod_aliud_de_multiplum(
...    'rem_statum',
...    ['lat_rem_finale', 'UTX_provisional', 'XLIFF_initial'])
>>> testum_I
{'_conjecturum': ['TBX_preferred'], '_crudum_originale': \
['lat_rem_finale', 'UTX_provisional', 'XLIFF_initial'], \
'codicem_TBX': 'preferred', \
'codicem_UTX': 'provisional', \
'codicem_XLIFF': 'initial', \
'codicem_lat': 'rem_finale'}


>>> testum_II = ontologia.quod_aliud_de_multiplum(
...    'rem_statum',
...    ['lat_rem_finale'])

>>> testum_II
{'_conjecturum': ['TBX_preferred', 'UTX_approved', 'XLIFF_final'], \
'_crudum_originale': ['lat_rem_finale'], \
'codicem_TBX': 'preferred', \
'codicem_UTX': 'approved', \
'codicem_XLIFF': 'final', \
'codicem_lat': 'rem_finale'}

        """
        if not aliud_valorem_multiplum or len(aliud_valorem_multiplum) == 0:
            return None

        if isinstance(aliud_valorem_multiplum, str):
            aliud_valorem_multiplum = list(map(
                str.strip,
                aliud_valorem_multiplum.split('|')))

        # aliud_valorem_multiplum.sort(key=str.lower)

        resultatum = {
            '_crudum_originale': aliud_valorem_multiplum,
            '_conjecturum': []
        }
        aliud_familiam = set(
            sorted(self.crudum['ontologia_aliud_familiam'].keys(),
                   key=str.lower)
        )

        aliud_secundum = set()
        for item in aliud_valorem_multiplum:
            rem = self.quod_aliud(aliud_typum, item)
            if rem is None or '_aliud_familiam' not in rem:
                # print('not in rem')
                continue
            resultatum['codicem_' + rem['_aliud_familiam']] = \
                rem['codicem_' + rem['_aliud_familiam']]
            aliud_familiam.discard(rem['_aliud_familiam'])
            if 'aliud' in rem and len(rem['aliud']) > 0:
                aliud_secundum.update(rem['aliud'])
            # print(rem['_aliud_familiam'])
            # aliud.append(rem)

        if len(aliud_secundum) > 0:
            # print('>0', aliud_secundum)
            for item in aliud_secundum:
                rem = self.quod_aliud(aliud_typum, item)
                if rem is None or '_aliud_familiam' not in rem:
                    continue
                if 'codicem_' + rem['_aliud_familiam'] in resultatum:
                    # print('iam exsistit: ', item)
                    continue

                # print('conjectūrum!: ', item)
                resultatum['_conjecturum'].append(item)
                resultatum['codicem_' + rem['_aliud_familiam']] = \
                    rem['codicem_' + rem['_aliud_familiam']]
                resultatum['_conjecturum'].sort(key=str.lower)

        resultatum = dict(OrderedDict(sorted(resultatum.items())))

        # print('')
        # print('resultatum', resultatum)
        # print('')

        return resultatum

    def quod_formatum_excerptum(self) -> Dict:
        """Quod fōrmātum excerptum?

        _[eng-Latn]
        Return fōrmātum excerptum (the formatum_excerptum from Ontologia)
        [eng-Latn]_

        Trivia:
            - fōrmātum, https://en.wiktionary.org/wiki/formatus#Latin
            - excerptum, https://en.wiktionary.org/wiki/excerptus#Latin

        Returns:
            Dict: fōrmātum excerptum
        """
        if self.crudum and 'formatum_excerptum' in self.crudum:
            return self.crudum['formatum_excerptum']
        return {}

    def quod_globum_valorem(self) -> Dict:
        """Quod globum valorem?

        _[eng-Latn]
        Return global variables (for Ontologia)
        [eng-Latn]_

        Trivia:
            - globum, https://en.wiktionary.org/wiki/globus#Latin
            - valōrem, https://en.wiktionary.org/wiki/valor#Latin

        Returns:
            Dict: globum valorem
        """
        # TODO: HXLTMOntologia.quod_globum_valorem is a draft.
        # resultatum = {}
        # return resultatum
        return self.crudum

    def quod_rem_statum(self,
                        statum_rem_accuratum: int = None,
                        statum_rem_textum: str = '',
                        rem_json: Union[str, Dict] = None
                        ) -> Dict:
        """[summary]

        Args:
            statum_rem_accuratum (int, optional):
                Statum rem accūrātum. Defallo Python None.
            statum_rem_textum (str, optional):
                Statum rem textum. Defallo vacuum textum.

        Returns:
            Dict: [description]
        """
        # pylint: disable=no-self-use
        # TODO: make the defaults configurable

        resultatum = {
            # 1-10, TBX uses it
            'accuratum': statum_rem_accuratum,
            # 'crudum': [],
            'crudum_originale': [],
            # initial, translated, reviewed, final
            'XLIFF': 'initial',
            # provisional, approved, '', non-standard, rejected, obsolete
            'UTX': 'provisional'
        }
        if rem_json:
            raise NotImplementedError('quod_rem_statum rem_json')

        if statum_rem_textum != '':
            crudum_originale = statum_rem_textum.split('|')
            resultatum['crudum_originale'] = crudum_originale

        # scālam, https://en.wiktionary.org/wiki/scala#Latin

        # TODO: implement this check
        return resultatum

    def quod_xml_typum(self,
                       radicem_tag: str,
                       radicem_attributum: dict = None
                       ) -> Dict:
        """quod_xml_typum Quod XML typum est?

        _[eng-Latn]
        TODO: make this method actually load the references from the
        *.hxltm.yml, so the users could have at least some freedom
        (as they already have when exporting) but now to import.
        [eng-Latn]_

        Args:
            radicem_tag (str):
                XML rādīcem (textum)
            radicem_attributum (dict, optional):
                HXL attribūtum de rādīcem. Defallo Python None

        Returns:
            Dict: typum, versiōnem, variāns
        """
        # pylint: disable=no-self-use
        resultatum = {
            'hxltm_normam': '',
            'typum': 'XML',
            # XLIFF 2.x may provide srcLang / trgLang on <xliff>
            'linguam_fontem': '',
            'linguam_fontem_attributum': '',
            'linguam_objectivum': '',
            'linguam_objectivum_attributum': '',
            'radicem_attributum_crudum': {},
            # variāns, https://en.wiktionary.org/wiki/varians#Latin
            'varians': '',
            'versionem': -1
        }

        # def hxl_attr(clavem):
        #     if not clavem or clavem.find('}') == -1:
        #         return clavem
        #     return clavem.split('}')[-1]

        attributum = radicem_attributum if radicem_attributum else {}
        if radicem_attributum:
            for clavem in list(radicem_attributum):
                clavem_basim = HXLTMUtil.xml_clavem_breve(clavem)
                if clavem_basim != clavem and \
                        clavem_basim not in radicem_attributum:
                    attributum[clavem_basim] = radicem_attributum[clavem]

            resultatum['radicem_attributum_crudum'] = \
                radicem_attributum
        radicem_tag_basim = HXLTMUtil.xml_clavem_breve(radicem_tag)

        # print('attributum', attributum)

        # print('quod_xml_typum', radicem_tag, radicem_attributum,
        # resultatum, radicem_tag_basim)
        if radicem_tag_basim == 'tmx':
            resultatum['hxltm_normam'] = 'TMX'
            resultatum['typum'] = 'TMX'
            resultatum['versionem'] = '1.4'
        if radicem_tag_basim == 'martif':
            resultatum['hxltm_normam'] = 'TBX-Basim'
            resultatum['typum'] = 'TBX'
            resultatum['versionem'] = 'TBX-Basic'
        if radicem_tag_basim == 'tbx':
            resultatum['hxltm_normam'] = 'TBX-IATE'
            resultatum['typum'] = 'TBX'
            resultatum['versionem'] = 'TBX-IATE'
        if radicem_tag_basim == 'xliff':
            resultatum['hxltm_normam'] = 'XLIFF'
            resultatum['typum'] = 'XLIFF'
            resultatum['linguam_fontem_attributum'] = 'srcLang'
            resultatum['linguam_objectivum_attributum'] = 'trgLang'
            if 'version' in attributum:
                resultatum['versionem'] = attributum['version']
                if str(resultatum['versionem']).startswith('1.'):
                    resultatum['hxltm_normam'] = 'XLIFF-obsoletum'
                    resultatum['linguam_fontem_attributum'] = 'lang'
                    resultatum['linguam_objectivum_attributum'] = 'lang'

        if 'version' in attributum:
            resultatum['versionem'] = attributum['version']

        if 'type' in attributum:
            resultatum['varians'] = attributum['type']

        if 'srcLang' in attributum:
            resultatum['linguam_fontem'] = attributum['srcLang']

        if 'trgLang' in attributum:
            resultatum['linguam_objectivum'] = attributum['trgLang']

        return resultatum

    def quod_xml_typum_tag(
        self,
        hxltm_normam: str
    ) -> Dict:
        """quod_xml_typum Quod XML typum est?

        _[eng-Latn]
        TODO: make this method actually load the references from the
        *.hxltm.yml, so the users could have at least some freedom
        (as they already have when exporting) but now to import.
        [eng-Latn]_

        Args:
            hxltm_normam (str):
                HXLTM normam (textum)

        Returns:
            Dict: typum, versiōnem, variāns
        """
        # pylint: disable=no-self-use
        resultatum = {
            'conceptum_signum': '',
            'conceptum_attributum': 'id',
            'fontem': '',
            'terminum': '',
            'objectivum': ''
        }

        if hxltm_normam == 'TBX-Basim':
            # <termEntry id="L10N_ego_codicem">
            #     <langSet xml:lang="la">
            #         <tig>
            #           <term>lat-Latn</term>
            #         </tig>
            #     </langSet>
            # </termEntry>
            resultatum['conceptum_signum'] = 'termEntry'
            resultatum['terminum'] = 'langSet/tig/term'

        if hxltm_normam == 'TBX-IATE':
            # <conceptEntry id="254003">
            #     <descrip type="subjectField">linguistics</descrip>
            #     <langSec xml:lang="es">
            #         <termSec>
            #             <term>acto de habla indirecto</term>
            #             <termNote type="termType">fullForm</termNote>
            #             <descrip type="reliabilityCode">1</descrip>
            #         </termSec>
            #     </langSec>
            # </conceptEntry>
            resultatum['conceptum_signum'] = 'conceptEntry'
            resultatum['terminum'] = 'langSec/termSec/term'
        if hxltm_normam == 'TMX':
            # <tu tuid="L10N_ego_codicem">
            #   <tuv xml:lang="la">
            #     <seg>lat-Latn</seg>
            #   </tuv>
            # </tu>
            resultatum['conceptum_signum'] = 'tu'
            resultatum['conceptum_attributum'] = 'tuid'  # Non 'id'
            resultatum['terminum'] = 'tuv/seg'

        if hxltm_normam == 'XLIFF':
            # <xliff version="2.0"
            #   xmlns="urn:oasis:names:tc:xliff:document:2.0"
            #   xmlns:fs="urn:oasis:names:tc:xliff:fs:2.0"
            #   xmlns:val="urn:oasis:names:tc:xliff:validation:2.0"
            #   srcLang="pt"
            #   trgLang="es">
            #
            # (...)
            #
            #   <unit id="L10N_ego_scriptum_nomen">
            #       <segment state="final">
            #           <source>Alfabeto latino</source>
            #           <target>Alfabeto latino</target>
            #       </segment>
            #   </unit>
            resultatum['conceptum_signum'] = 'unit'
            # resultatum['fontem'] = 'segment/source'
            resultatum['fontem'] = 'source'
            # resultatum['objectivum'] = 'segment/target'
            resultatum['objectivum'] = 'target'

        if hxltm_normam == 'XLIFF-obsoletum':
            # <trans-unit id="L10N_ego_codicem" translate="no" approved="yes">
            #     <source>por-Latn</source>
            #     <target state="final">spa-Latn</target>
            #     <note annotates="source" priority="2">
            #     _    [eng-Latn]eng-Latn[eng-Latn]_
            #     </note>
            # </trans-unit>
            resultatum['conceptum_signum'] = 'trans-unit'
            resultatum['fontem'] = 'source'
            resultatum['objectivum'] = 'target'

        return resultatum

    @staticmethod
    def quid_est_hashtag_circa_conceptum(
            hxl_hashtag: str) -> Union[bool, None]:
        """Quid est hashtag circa +conceptum?

        _[eng-Latn]
        Is this hashtag about concept level?
        [eng-Latn]

        Args:
            hxl_hashtag (str): Hashtag ad textum

        Returns:
            bool:
        """
        # TODO: make this actually read the cor.hxltm.215.yml. This hardcoded
        #       part is just a quick fix

        if HXLTMOntologia.quid_est_hashtag_circa_linguam_aut_terminum(hxl_hashtag):
            return False

        if hxl_hashtag.find('+conceptum') > -1:
            return True

        return False

    @staticmethod
    def quid_est_hashtag_circa_linguam_aut_terminum(hxl_hashtag: str) -> bool:
        """Quid est hashtag circa linguam?

        _[eng-Latn]
        Is this hashtag about language term?
        [eng-Latn]

        Args:
            hxl_hashtag (str): Hashtag ad textum

        Returns:
            bool:
        """
        # TODO: make this actually read the cor.hxltm.215.yml. This hardcoded
        #       part is just a quick fix

        if hxl_hashtag.startswith('#item+linguam'):
            return True
        if hxl_hashtag.startswith('#meta+linguam'):
            return True

        if hxl_hashtag.startswith('#item+rem+i_'):
            return True
        if hxl_hashtag.startswith('#meta+rem+i_'):
            return True
        if re.match(r"\#.*(\+i_).*(\+is_).*", hxl_hashtag):
            # # +i_ +is_
            return True
        return False

    def quod_nomen_breve_de_hxl(self, hxl_hashtag: str) -> str:
        # TODO: make this actually read the cor.hxltm.215.yml. This hardcoded
        #       part is just a quick fix

        # TODO: some types on cor.hxltm.215.yml are actually not string, but
        #       lists. This means when asked, we should allow give
        #       hints to let these values be converted
        nomen_breve = ''
        if hxl_hashtag == '#item+conceptum+codicem':
            nomen_breve = 'conceptum_codicem'

        if hxl_hashtag == '#meta+conceptum+codicem+alternativum':
            nomen_breve = 'codicem_alternativum'

        elif hxl_hashtag == '#item+conceptum+dominium':
            nomen_breve = 'conceptum_dominium'

        elif hxl_hashtag == '#meta+item+url+list':
            # conceptum.referens_situs_interretialis
            nomen_breve = 'referens_situs_interretialis'

        elif hxl_hashtag == '#item+conceptum+typum':
            nomen_breve = 'conceptum_typum'

        elif hxl_hashtag.startswith('#status+rem+accuratum+i_'):
            nomen_breve = 'accuratum__L__'

        elif hxl_hashtag.startswith('#status+rem+textum+i_'):
            nomen_breve = 'statum_rem_textum__L__'

        elif hxl_hashtag.startswith('#status+rem+json+i_'):
            nomen_breve = 'statum_rem_json__L__'

        elif hxl_hashtag.startswith('#item+rem+i_'):
            nomen_breve = 'rem__L__'

        return nomen_breve

    def quod_nomen_breve_de_id(self, _hxl_hashtag: str) -> str:
        """TODO quod_nomen_breve_de_id
        """
        # pylint: disable=no-self-use
        return ''

    # def in_rem(self, focused_datum: List) -> Type['HXLTMRem']:
    #     # TODO: make a version of HXLTMRem that supports multiple values
    #     #       grouped, and already initialized with lanuage tag, not
    #     #       raw hashtag, since several terms would have
    #     #       several hashtags
    #     pass


class HXLTMUtil:
    """HXL Trānslātiōnem Memoriam auxilium programmi

    Author:
            Emerson Rocha <rocha[at]ieee.org>
    Creation date:
            2021-06-09
    """

    @staticmethod
    def bcp47_from_hxlattrs(hashtag: Union[str, None]) -> str:
        """From a typical HXLTM hashtag, return only the bcp47 language code
        without require a complex table equivalence.

        Example:
            >>> HXLTMUtil.bcp47_from_hxlattrs('#item+i_ar+i_arb+is_arab')
            'ar'
            >>> HXLTMUtil.bcp47_from_hxlattrs('#item+i_arb+is_arab')
            ''

        Args:
            linguam ([String]): A linguam code

        Returns:
            [String]: HXL Attributes
        """
        if hashtag and isinstance(hashtag, str):
            parts = hashtag.lower().split('+i_')
            for k in parts:
                if len(k) == 2:
                    return k

        return ''

    @staticmethod
    def bcp47_from_linguam(linguam: Union[str, None]) -> str:
        """From am linguam with hint about BCP47, get the BCP47 code
        Returns empty if no hint exist

        Example:
            >>> HXLTMUtil.bcp47_from_hxlattrs('por-Latn')
            ''
            >>> HXLTMUtil.bcp47_from_linguam('por-Latn@pt')
            'pt'
            >>> HXLTMUtil.bcp47_from_linguam('por-Latn@pt-BR')
            'pt-BR'

        Args:
            linguam ([String]): A linguam code

        Returns:
            [String]: HXL Attributes
        """
        if linguam.find('@') > -1:
            _linguam, bcp47 = list(linguam.split('@'))
            return bcp47

        return ''

    @staticmethod
    def conceptum_saccum(
        valorem: str,
        libellam_et_typum: str = 'terminum.valorem',
        linguam_crudum_aut_typum: str = None,
        saccum: Dict = None,
        unicum: bool = True
    ) -> Dict:  # pylint: disable=no-self-use
        """conceptum_saccum

        _[eng-Latn]
        conceptum_saccum is a simple helper (uses plain Python Dict) to
        abstract a concept bag.

        This is mostly used on hxltmdexml (for importing data from XML)
        [eng-Latn]_

        Args:
            valorem (str):
                Rem valōrem
            libellam_et_typum (str):
                typum de Rem valōrem. Exemplum:
                    - conceptum.codicem
                    - linguam.partem_orationis / terminum.partem_orationis
                    - terminum.valorem
                    - terminum.accuratum
            linguam_crudum_aut_typum (str):
                Linguam clāvem textum crudum (exemplum: por-Latn, spa-Latn)
                aut typum (exemplum: fontem, objectivum)
            saccum (Dict):
                conceptum saccum, de Python Dict
            valorem_multiplum (bool):
                Valōrem est ūnicum? Devallo verum.

        Returns:
            Dict:

>>> HXLTMUtil.conceptum_saccum(
...    'test', 'terminum.terminum', 'por-Latn')
{'terminum': {'por-Latn': {'terminum': 'test'}}}

>>> HXLTMUtil.conceptum_saccum(
...    'C1', 'conceptum.codicem')
{'conceptum': {'codicem': 'C1'}}

>>> HXLTMUtil.conceptum_saccum(
...    'C1', 'conceptum.codicem_alternativum', unicum=False)
{'conceptum': {'codicem_alternativum': ['C1']}}
        """
        # @see https://terminator.readthedocs.io/en/latest
        #      /_images/TBX_termEntry_structure.png
        # id est, terminum de terminum.valorem
        # print(libellam_et_typum)
        # return ''
        # libellam, typum, *rest = libellam_et_typum.split('.')
        libellam, typum = libellam_et_typum.split('.')

        if saccum is None:
            saccum = {}

        if libellam not in saccum:
            saccum[libellam] = {}

        if libellam in ['linguam', 'terminum']:
            if not linguam_crudum_aut_typum:
                raise ValueError(
                    'non linguam_crudum de {0}'.format(valorem))

            if linguam_crudum_aut_typum not in saccum[libellam]:
                saccum[libellam][linguam_crudum_aut_typum] = {}

            if unicum:
                saccum[libellam][linguam_crudum_aut_typum][typum] = valorem
            else:
                if typum not in saccum[libellam][linguam_crudum_aut_typum]:
                    saccum[libellam][linguam_crudum_aut_typum][typum] = []
                saccum[libellam][linguam_crudum_aut_typum][typum].append(
                    valorem
                )
            # if libellam == 'terminum':
                # if typum not in saccum[libellam][linguam_crudum_aut_typum]:

        else:
            if unicum:
                saccum[libellam][typum] = valorem
            else:
                if typum not in saccum[libellam]:
                    saccum[libellam][typum] = []
                saccum[libellam][typum].append(
                    valorem
                )
            # saccum[libellam][typum] = valorem
            # conceptum est
            # pass

        return saccum

    @staticmethod
    def hxllangattrs_list_from_item(item):
        """hxllangattrs_list_from_item get only the raw attr string part
        that is repeated severa times and mean the same logical group.

        Example:
            >>> item = {'#item+i_pt+i_por+is_latn':
            ...          '','#item+i_pt+i_por+is_latn+alt+list': '',
            ...           '#meta+item+i_pt+i_por+is_latn': ''}
            >>> HXLTMUtil.hxllangattrs_list_from_item(item)
            {'+i_pt+i_por+is_latn'}

        Args:
            item ([Dict]): An dict item
        Returns:
            [Set]: Set of unique HXL language attributes
        """
        result = set()

        for k in item:
            rawstr = ''
            bcp47 = HXLTMUtil.bcp47_from_hxlattrs(k)
            iso6393 = HXLTMUtil.iso6393_from_hxlattrs(k)
            iso115924 = HXLTMUtil.iso115924_from_hxlattrs(k)
            if bcp47:
                rawstr += '+i_' + bcp47.lower()
            if iso6393:
                rawstr += '+i_' + iso6393.lower()
            if iso115924:
                rawstr += '+is_' + iso115924.lower()
            # print('   ', k, '   ', rawstr)
            result.add(rawstr)
        return result

    @staticmethod
    def iso6393_from_hxlattrs(hashtag: Union[str, None]) -> str:
        """From a typical HXLTM hashtag, return only the ISO 639-3 language
        code without require a complex table equivalence.

        Example:
>>> HXLTMUtil.iso6393_from_hxlattrs('#item+i_ar+i_arb+is_arab')
'arb'
>>> HXLTMUtil.iso6393_from_hxlattrs('#item+i_ar')
''
>>> HXLTMUtil.iso6393_from_hxlattrs('#item+i_pt+i_por+is_latn+alt+list')
'por'

        Args:
            hashtag ([String]): A hashtag string

        Returns:
            [String]: HXL Attributes
        """
        if hashtag and isinstance(hashtag, str):
            # parts = hashtag.lower().split('+i_')
            parts = hashtag.lower().split('+')
            # '#item+i_ar+i_arb+is_arab' => ['#item', 'ar', 'arb+is_arab']
            # print(parts)
            for k in parts:
                # if len(k) == 5 and k.find('+i_') == 0:
                if len(k) == 5 and k.startswith('i_'):
                    # print(k.find('i_'))
                    return k.replace('i_', '')

        return ''

    @staticmethod
    def iso115924_from_hxlattrs(hashtag: Union[str, None]) -> str:
        """From a typical HXLTM hashtag, return only the ISO 115924
        writting system without require a complex table equivalence.

        Example:
            >>> HXLTMUtil.iso115924_from_hxlattrs('#item+i_ar+i_arb+is_ARaB')
            'Arab'

            >>> HXLTMUtil.iso115924_from_hxlattrs('#item+i_pt')
            ''

        Args:
            hashtag ([String]): A linguam code

        Returns:
            [String]: HXL Attributes
        """
        if hashtag and isinstance(hashtag, str):
            parts = hashtag.lower().split('+')
            for k in parts:
                if k.startswith('is_'):
                    # return k.replace('is_', '')
                    return k.replace('is_', '').capitalize()
                    # return k.replace('is_', '').lower()

        return ''

    @staticmethod
    def linguam_2_hxlattrs(linguam):
        """linguam_2_hxlattrs

        Example:
            >>> HXLTMUtil.linguam_2_hxlattrs('por-Latn')
            '+i_por+is_latn'
            >>> HXLTMUtil.linguam_2_hxlattrs('por-Latn@pt')
            '+i_pt+i_por+is_latn'
            >>> HXLTMUtil.linguam_2_hxlattrs('por-Latn@pt-BR')
            '+i_pt+i_por+is_latn'
            >>> HXLTMUtil.linguam_2_hxlattrs('arb-Arab')
            '+i_arb+is_arab'

        Args:
            linguam ([String]): A linguam code

        Returns:
            [String]: HXL Attributes
        """
        if linguam.find('@') == -1:
            iso6393, iso115924 = list(linguam.lower().split('-'))
            return '+i_' + iso6393 + '+is_' + iso115924

        linguam, bcp47 = list(linguam.lower().split('@'))
        iso6393, iso115924 = list(linguam.split('-'))

        if bcp47.find('-') == -1:
            return '+i_' + bcp47 + '+i_' + iso6393 + '+is_' + iso115924

        # TODO: decide how to express country with hashtags
        iso6391, _adm = list(bcp47.split('-'))

        return '+i_' + iso6391 + '+i_' + iso6393 + '+is_' + iso115924

    @staticmethod
    def linguam_de_hxlhashtag(
            hxl_hashtag: str,
            non_obsoletum: bool = False,
            non_patriam: bool = False,
            non_privatum: bool = False) -> Union[str, None]:
        """Linguam de HXL hashtag

        Args:
            linguam ([str]): _[eng-Latn] An HXL hashtag [eng-Latn]_
            non_obsoletum ([bool]): Non bcp47?
            non_patriam ([bool]): Non patriam codicem??
            non_privatum ([bool]): Non privatum codicem?

        Returns:
            [Union[str, None]]: Linguam codicem aut python None

        Example:
            >>> HXLTMUtil.linguam_de_hxlhashtag(
            ...    '#meta+item+i_la+i_lat+is_latn')
            'lat-Latn@la'
        """
        rawstr = ''
        bcp47 = HXLTMUtil.bcp47_from_hxlattrs(hxl_hashtag)
        iso6393 = HXLTMUtil.iso6393_from_hxlattrs(hxl_hashtag)
        iso115924 = HXLTMUtil.iso115924_from_hxlattrs(hxl_hashtag)

        if non_patriam:
            # TODO: implement +ii_ (region with political influence attribute)
            raise NotImplementedError('non_patriam')
        if non_privatum:
            # TODO: implement +ix_ (private attributes)
            raise NotImplementedError('non_privatum')

        if iso6393:
            rawstr += iso6393
        if iso115924:
            rawstr += '-' + iso115924
        if bcp47 and not non_obsoletum:
            rawstr += '@' + bcp47

        return rawstr if rawstr else None

    @staticmethod
    def load_hxltm_options(custom_file_option=None, is_debug=False):
        """Load options from cor.hxltm.215.yml

        Args:
            custom_file_option ([str], optional): Custom options.
                    Defaults to None.
            is_debug (bool, optional): Is debug enabled? Defaults to False.

        Returns:
            [Dict]: Dictionary of cor.hxltm.215.yml contents
        """
        # pylint: disable=using-constant-test
        if is_debug:
            print('load_hxltm_options')
            print('HXLTM_DORMUM', HXLTM_DORMUM)
            print('HXLTM_SYSTEMA_DIR', HXLTM_SYSTEMA_DIR)
            print('HXLTM_RUNNING_DIR', HXLTM_RUNNING_DIR)

        if custom_file_option is not None:
            if Path(custom_file_option).exists():
                return HXLTMUtil._load_hxltm_options_file(
                    custom_file_option, is_debug)
            raise RuntimeError("Configuration file not found [" +
                               custom_file_option + "]")

        if Path(HXLTM_RUNNING_DIR + '/cor.hxltm.215.yml').exists():
            return HXLTMUtil._load_hxltm_options_file(
                HXLTM_RUNNING_DIR + '/cor.hxltm.215.yml', is_debug)

        if Path(HXLTM_DORMUM + '/cor.hxltm.215.yml').exists():
            return HXLTMUtil._load_hxltm_options_file(
                HXLTM_DORMUM + '/cor.hxltm.215.yml', is_debug)

        if Path(HXLTM_SYSTEMA_DIR + '/cor.hxltm.215.yml').exists():
            return HXLTMUtil._load_hxltm_options_file(
                HXLTM_SYSTEMA_DIR + '/cor.hxltm.215.yml', is_debug)

        raise RuntimeError(
            "EXITUM_ERROREM: cor.hxltm.215.yml? 1 HXLTM_RUNNING_DIR [{0}], " +
            "2 HXLTM_DORMUM [{1}], 3 HXLTM_SYSTEMA_DIR [{2}]".format(
                HXLTM_RUNNING_DIR, HXLTM_DORMUM, HXLTM_SYSTEMA_DIR)
        )

    @staticmethod
    def _load_hxltm_options_file(file, is_debug=False):
        if is_debug:
            print('_load_hxltm_options_file: [' + file + ']')

        with open(file, "r") as read_file:
            data = yaml.safe_load(read_file)
            return data

    @staticmethod
    def xliff_item_relevant_options(item):
        """From an dict (python object) return only keys that start with
        # x_xliff

        Args:
            item ([Dict]): An non-filtered dict (python object) represent a row

        Returns:
            [Dict]: A filtered object. ∅ is replaced by python None
        """
        item_neo = {}

        for k in item:
            if k.startswith('#x_xliff'):
                if item[k] == '∅':
                    item_neo[k] = None
                else:
                    item_neo[k] = item[k]

        return item_neo

    @staticmethod
    def tmx_item_relevan_options(item):
        return item

    @staticmethod
    def xliff_item_xliff_source_key(item):
        for k in item:
            if k.startswith('#x_xliff+source'):
                return k

        return None

    @staticmethod
    def xliff_item_xliff_target_key(item):
        for k in item:
            if k.startswith('#x_xliff+target'):
                return k

        return None

    @staticmethod
    def xml_clavem_breve(clavem):
        """xml_clavem_breve XML clāvem non-NS

        Args:
            clavem ([str]): XML clāvem

        Returns:
            [str]:

            >>> HXLTMUtil.xml_clavem_breve(
            ...    '{urn:oasis:names:tc:xliff:document:2.0}version')
            'version'
        """
        if not clavem or clavem.find('}') == -1:
            return clavem
        return clavem.split('}')[-1]


class HXLTMTestumAuxilium:
    """HXLTM Testum Auxilium

    _[eng-Latn]
    This class only contains static methods to help test the rest of the huge
    hxltmcli.py file.

    Every time lines start with ">>> python-code-here" this actually is an
    python doctest operation that can be executed with something like

        python3 -m doctest hxlm/core/bin/hxltmcli.py

    So the HXLTMTestumAuxilium contain test helpers.
    [eng-Latn]_

    Trivia:
    - testum, https://en.wiktionary.org/wiki/testum
    - auxilium, https://en.wiktionary.org/wiki/auxilium#Latin
    - disciplīnam manuāle
      - Python doctest
        - https://docs.python.org/3/library/doctest.html
    """

    @staticmethod
    def testum_praefixum(archivum: str = None) -> str:
        """Testum basim

        _[eng-Latn]
        Note: this will try check if the enviroment variable
        HXLTM_TESTUM and only fallback to assume the entire
        hdp-toolchain installation (or a fork from
        EticaAI/HXL-Data-Science-file-formats) on local disk.

        Since the hxltmclitm v0.8.2 can be used in standalone more, users
        may want to run tests from other paths (in special if they
        eventually want to propose for the public project)
        [eng-Latn]_

        Trivia:
        - archīvum, https://en.wiktionary.org/wiki/archivum
        - praefīxum, https://en.wiktionary.org/wiki/praefixus#Latin

        Returns:
            str:
                _[eng-Latn]
                Directory containing test files.
                [eng-Latn]_
        """

        # if HDATUM_EXEMPLUM:
        # hxltmtestum = str(Path(
        #     HXLTM_SYSTEMA_DIR + '/../../../testum/hxltm').resolve())

        praefixum = os.getenv('HXLTM_TESTUM', HXLTM_TESTUM)

        if archivum:
            return praefixum + '/' + archivum

        return praefixum

    @staticmethod
    def datum(
        exemplum_archivum: str = 'hxltm-exemplum-linguam.tm.hxl.csv'
    ) -> List:
        """Crudum HXLTM exemplum datum

        Returns:
            List: Crudum HXLTM exemplum datum
        """
        if not os.path.isfile(exemplum_archivum):
            exemplum_archivum = HXLTMTestumAuxilium.testum_praefixum(
                exemplum_archivum)

        if not os.path.isfile(exemplum_archivum):
            raise RuntimeError(
                'HXLTMTestumAuxilium non-datum [{}]. '
                'Requīsītum: dēfīnītiōnem HXLTM_TESTUM. Exemplum:'
                '> HXLTM_TESTUM="/home/marcus/testum/" '
                'python3 -m doctest hxltmcli-de-marcus.py'
                ' <'.format(exemplum_archivum))

        hxltm_crudum = []
        with open(exemplum_archivum, 'r') as arch:
            csv_lectorem = csv.reader(arch)
            for rem in csv_lectorem:
                hxltm_crudum.append(rem)
            # hxltm_crudum = arch.read().splitlines()

        # print(hxltm_crudum)
        return hxltm_crudum

    @staticmethod
    def ontologia() -> Dict:
        """HXLTM Ontologia 'cor.hxltm.215.yml'

        Returns:
            Dict: HXLTM Ontologia
        """
        conf = HXLTMUtil.load_hxltm_options()
        # print(ontologia.keys())
        # print(ontologia)
        # print(HXLTMUtil.load_hxltm_options()['normam'])
        # return HXLTMUtil.load_hxltm_options()
        return HXLTMOntologia(conf)


class XMLInFormatumHXLTM():
    """HXLTM In Fōrmātum; abstractum Python classem

    Trivia:
        - HXLTM:
        - HXLTM, https://hdp.etica.ai/hxltm
            - HXL, https://hxlstandard.org/
            - TM, https://www.wikidata.org/wiki/Q333761
        - in, https://en.wiktionary.org/wiki/in-#Latin
        - fōrmātum, https://en.wiktionary.org/wiki/formatus#Latin
        - abstractum Python classem
            - abstractum, https://en.wiktionary.org/wiki/abstractus#Latin
            - Python, https://docs.python.org/
            - classem, https://en.wiktionary.org/wiki/classis#Latin
        - disciplīnam manuāle
            - https://docs.python.org/3/library/abc.html

    Intrōductōrium cursum de Latīnam linguam (breve glōssārium):
        - archīvum, https://en.wiktionary.org/wiki/archivum
        - datum, https://en.wiktionary.org/wiki/datum#Latin
        - contextum, https://en.wiktionary.org/wiki/contextus#Latin
        - corporeum, https://en.wiktionary.org/wiki/corporeus#Latin
        - collēctiōnem, https://en.wiktionary.org/wiki/collectio#Latin
            - id est: Python List
        - dē, https://en.wiktionary.org/wiki/de#Latin
        - errōrem, https://en.wiktionary.org/wiki/error#Latin
        - fīnāle, https://en.wiktionary.org/wiki/finalis#Latin
        - 'id est', https://en.wiktionary.org/wiki/id_est
        - initiāle, https://en.wiktionary.org/wiki/initialis#Latin
        - locum, https://en.wiktionary.org/wiki/locum#Latin
        - resultātum, https://en.wiktionary.org/wiki/resultatum

    Speciāle verbum in HXLTM:
        - 'Exemplōrum gratiā (et Python doctest, id est, testum automata)'
            - Exemplōrum gratiā
              - https://en.wikipedia.org/wiki/List_of_Latin_phrases_(full)
            - 'Python doctest' (non Latīnam)
                -https://docs.python.org/3/library/doctest.html

    Author:
        Multis Clanculum Civibus

    Collaborators:
        Emerson Rocha <rocha[at]ieee.org>

    Creation Date:
        2021-07-24

    Revisions:

    License:
        Public Domain

    Args:
        ontologia (HXLTMOntologia):
            HXLTMASA objectīvum
        fontem_archivum (str):
        objectvum_archivum (str):
    """

    # # # ontologia/cor.hxltm.215.yml clāvem nomen
    # # ONTOLOGIA_FORMATUM = ''

    # # ontologia/cor.hxltm.215.yml basim extēnsiōnem
    # ONTOLOGIA_NORMAM: str = ''

    # # Trivia: speciāle, https://en.wiktionary.org/wiki/specialis#Latin
    # ontologia_normam_speciale = ''

    # hxltm_asa
    # ontologia
    _ontologia: Type['HXLTMOntologia'] = None

    # linguam_collectionem = []
    # linguam_agendum: Type[List['HXLTMLinguam']] = None
    agendum_linguam: Type[List['HXLTMLinguam']] = []
    agendum_attributum: Type[List[str]] = [],
    fontem_linguam: Type['HXLTMLinguam'] = None
    objectivum_linguam: Type['HXLTMLinguam'] = None

    # de_rem_accuratum: bool = True
    _habendum_accuratum: bool = False
    _habendum_typum: bool = False

    # TODO: remove this gambiarra
    temporary_fix = {
        'pt': 'por-Latn@pt',
        'en': 'eng-Latn@en',
        'es': 'spa-Latn@es',
        'eo': 'epo-Latn@eo',
        'sk': 'slk-Latn@sk',
    }

    # __commune_asa: InitVar[Type['HXLTMASA']] = None

    # @see https://docs.python.org/3/library/logging.html
    # @see https://docs.python.org/pt-br/dev/howto/logging.html

    def __init__(
        self,
        ontologia: Type['HXLTMOntologia'],
        agendum_linguam: Type[List['HXLTMLinguam']] = None,
        agendum_attributum: Type[List[str]] = None,
        # agendum_attributum: Type[List['str']] = [],
        fontem_linguam: Type['HXLTMLinguam'] = None,
        objectivum_linguam: Type['HXLTMLinguam'] = None
    ):
        """__init__

        Args:
            ontologia (HXLTMOntologia): ontologia
        """
        self._ontologia = ontologia
        if agendum_linguam:
            self.agendum_linguam = agendum_linguam

        if agendum_attributum:
            self.agendum_attributum = agendum_attributum

        if fontem_linguam:
            self.fontem_linguam = fontem_linguam

        if objectivum_linguam:
            self.objectivum_linguam = objectivum_linguam
        # print(self.linguam_agendum)
        # print(self.fontem_linguam.v())
        # print(self.objectivum_linguam.v())

    def definitionem_habendum_accuratum(
            self,
            habendum_accuratum: bool = True) -> Type['XMLInFormatumHXLTM']:
        """dēfīnītiōnem habendum accuratum?

        _[eng-Latn]
        Use this to give a hint that the XML do have option to parse
        reliability of the term
        [eng-Latn]_

        Returns:
            [XMLInFormatumHXLTM]:
        """

        self._habendum_accuratum = bool(habendum_accuratum)

        return self

    def definitionem_habendum_typum(
            self,
            habendum_typum: bool = True) -> Type['XMLInFormatumHXLTM']:
        """dēfīnītiōnem habendum typum?

        _[eng-Latn]
        Use this to give a hint that the XML do have option to parse
        type of the term
        [eng-Latn]_

        Returns:
            [XMLInFormatumHXLTM]:
        """

        self._habendum_typum = bool(habendum_typum)

        return self

    def definitionem_linguam(
            self, linguam: str) -> Type['XMLInFormatumHXLTM']:
        """dēfīnītiōnem linguam

        _[eng-Latn]
        NOTE: all the languages need to be know upfront (even it if means)
        peak part of the XML file) to be able to generate output.

        Add new languages that were not defined will not work.

        Add a new language after the heading files was created, will also
        generate a CSV-like file with more columns (id est, invalid).
        [eng-Latn]_

        Returns:
            [XMLInFormatumHXLTM]:
        """
        if linguam is False:
            # Used to reset
            self.agendum_linguam = []
            return self

        if len(linguam) == 5 and linguam.find('-') > -1:
            linguam = linguam.split('-')[0]

        if len(linguam) == 2 and linguam in self.temporary_fix:
            linguam = self.temporary_fix[linguam]
            # if linguam

        self.agendum_linguam.append(
            HXLTMLinguam(linguam)
        )
        return self

    def definitionem_linguam_fontem(
            self, linguam: str) -> Type['XMLInFormatumHXLTM']:
        """dēfīnītiōnem linguam fontem

        Returns:
            [XMLInFormatumHXLTM]:
        """

        if linguam is False:
            # Used to reset
            self.fontem_linguam = False
            return self

        if len(linguam) == 5 and linguam.find('-') > -1:
            linguam = linguam.split('-')[0]

        if len(linguam) == 2 and linguam in self.temporary_fix:
            linguam = self.temporary_fix[linguam]

        self.fontem_linguam = HXLTMLinguam(linguam)
        return self

    def definitionem_linguam_objectivum(
            self, linguam: str) -> Type['XMLInFormatumHXLTM']:
        """dēfīnītiōnem linguam objectivum

        Returns:
            [XMLInFormatumHXLTM]:
        """

        if linguam is False:
            # Used to reset
            self.objectivum_linguam = False
            return self

        if len(linguam) == 5 and linguam.find('-') > -1:
            linguam = linguam.split('-')[0]

        if len(linguam) == 2 and linguam in self.temporary_fix:
            linguam = self.temporary_fix[linguam]

        self.objectivum_linguam = HXLTMLinguam(linguam)
        return self

    def in_caput(self):
        resultatum = []
        # if 'rem' in self.agendum_attributum:
        resultatum.append('#item+conceptum+codicem')

        # print('self.agendum_attributum', self.agendum_attributum)
        if 'indicem_de_terminum' in self.agendum_attributum:
            resultatum.append('#item+conceptum+indicem_de_terminum')

        if 'meta' in self.agendum_attributum or \
                'meta_conceptum' in self.agendum_attributum:
            resultatum.append('#meta+conceptum')

        # print('self.agendum_attributum', str(self.agendum_attributum[0]))
        if self.fontem_linguam:
            resultatum.append('#item+rem' + self.fontem_linguam.a())
            if self._habendum_accuratum:
                resultatum.append(
                    '#item+rem+accuratum' + self.fontem_linguam.a())
            if 'meta' in self.agendum_attributum or \
                    'meta_linguam' in self.agendum_attributum:
                resultatum.append('#meta+linguam' + self.fontem_linguam.a())

        if self.objectivum_linguam:
            resultatum.append('#item+rem' + self.objectivum_linguam.a())
            if self._habendum_accuratum:
                resultatum.append(
                    '#item+rem+accuratum' + self.objectivum_linguam.a())
            if 'meta' in self.agendum_attributum or \
                    'meta_linguam' in self.agendum_attributum:
                resultatum.append('#meta+linguam' +
                                  self.objectivum_linguam.a())

        for linguam in self.agendum_linguam:

            if 'meta' in self.agendum_attributum or \
                    'meta_linguam' in self.agendum_attributum:
                resultatum.append('#meta+linguam' + linguam.a())

            resultatum.append('#item+rem' + linguam.a())
            if self._habendum_accuratum:
                resultatum.append('#status+rem+accuratum' + linguam.a())
            if self._habendum_typum:
                resultatum.append('#status+terminum+typum' + linguam.a())

            if 'meta' in self.agendum_attributum or \
                    'meta_terminum' in self.agendum_attributum:
                resultatum.append('#meta+terminum' + linguam.a())

        return resultatum

    def in_lineam(
        self,
        conceptum_codicem: str = '',
        fontem_textum: str = '',
        objectivum_textum: str = '',
        fontem_accuratum: str = '',
        objectivum_accuratum: str = '',
        terminum: list = None
    ):
        """in_lineam

        @deprecated eventually convert last uses to
        in_lineam_de_conceptum_sacuum()

        Args:
            conceptum_codicem (str, optional): [description]. Defaults to ''.
            fontem_textum (str, optional): [description]. Defaults to ''.
            objectivum_textum (str, optional): [description]. Defaults to ''.
            fontem_accuratum (str, optional): [description]. Defaults to ''.
            objectivum_accuratum (str, optional): [description].Defaults to ''.
            terminum (list, optional): [description]. Defaults to None.

        Returns:
            [list]:
        """
        # pylint: disable=no-self-use
        resultatum = [conceptum_codicem]
        if fontem_textum:
            resultatum.append(fontem_textum)
        if objectivum_textum:
            resultatum.append(objectivum_textum)

        # TODO: if previously was added accuraty, make it add even
        #       if empty
        if fontem_accuratum:
            resultatum.append(fontem_accuratum)
        if objectivum_accuratum:
            resultatum.append(objectivum_accuratum)

        return resultatum

    def in_lineam_de_conceptum_sacuum(
        self,
        conceptum_sacuum: Dict
    ) -> List[List]:
        """in_lineam_de_conceptum_sacuum

        Args:
            conceptum_sacuum (Dict):
                Python Dict. @see HXLTMUtil.conceptum_saccum()

        Returns:
            List[List]: [description]
        """
        resultatum = []

        # TODO: remove a lot of redundancy from this method.

        if not conceptum_sacuum or \
                'conceptum' not in conceptum_sacuum or \
                'codicem' not in conceptum_sacuum['conceptum']:
            raise ValueError(
                'non conceptum.codicem ad {0}'.format(str(conceptum_sacuum)))

        lineam_1 = []

        # print(self.linguam_fontem)
        # print(conceptum_sacuum)

        lineam_1.append(
            conceptum_sacuum['conceptum']['codicem']
        )

        # print('self.agendum_attributum2', self.agendum_attributum)
        if 'indicem_de_terminum' in self.agendum_attributum:
            # For now, it's hardcoded 1 but later should be rewriten to allow
            # multiple terms entry
            lineam_1.append("1")

        if 'meta' in self.agendum_attributum or \
                'meta_conceptum' in self.agendum_attributum:
            # resultatum.append('#meta+conceptum')
            # For now, it's hardcoded empty string, but later should be
            # rewriten to add explicitly metadata or anything not explicity
            # exported by other means
            lineam_1.append("")

        # TODO: fix TBX/TMX that now may output fontem

        if self.fontem_linguam:
            lineam_1.append(self._ontologia.de(
                'terminum.fontem.valorem', fontem=conceptum_sacuum))
            if 'meta' in self.agendum_attributum or \
                    'meta_linguam' in self.agendum_attributum:
                # TODO: this is a draft. need to be implemented
                lineam_1.append("")

        if self.objectivum_linguam:
            lineam_1.append(self._ontologia.de(
                'terminum.objectivum.valorem', fontem=conceptum_sacuum))
            if 'meta' in self.agendum_attributum or \
                    'meta_linguam' in self.agendum_attributum:
                # TODO: this is a draft. need to be implemented
                lineam_1.append("")

        for linguam in self.agendum_linguam:
            # lineam_1.append('#item+rem' + linguam.a())
            valuem = ''

            if 'meta' in self.agendum_attributum or \
                    'meta_linguam' in self.agendum_attributum:
                # TODO: this is a draft. need to be implemented
                lineam_1.append("")

            if linguam.bcp47:
                valuem = self._ontologia.de(
                    'terminum.' + linguam.bcp47 + '.valorem',
                    fontem=conceptum_sacuum
                )

            elif linguam.iso6393:
                valuem = self._ontologia.de(
                    'terminum.' + linguam.iso6393 + '.valorem',
                    fontem=conceptum_sacuum
                )

            if not valuem:
                valuem = self._ontologia.de(
                    'terminum.' + linguam.linguam +
                    '.valorem',
                    fontem=conceptum_sacuum
                )

            lineam_1.append(valuem)

            if self._habendum_accuratum:
                valuem = ''
                if linguam.bcp47:
                    valuem = self._ontologia.de(
                        'terminum.' + linguam.bcp47 +
                        '.accuratum',
                        fontem=conceptum_sacuum
                    )

                elif linguam.iso6393:
                    valuem = self._ontologia.de(
                        'terminum.' + linguam.iso6393 +
                        '.accuratum',
                        fontem=conceptum_sacuum
                    )

                if not valuem:
                    valuem = self._ontologia.de(
                        'terminum.' + linguam.linguam +
                        '.accuratum',
                        fontem=conceptum_sacuum
                    )

                lineam_1.append(valuem)

            if self._habendum_typum:
                valuem = ''
                if linguam.bcp47:
                    valuem = self._ontologia.de(
                        'terminum.' + linguam.bcp47 +
                        '.typum',
                        fontem=conceptum_sacuum
                    )

                elif linguam.iso6393:
                    valuem = self._ontologia.de(
                        'terminum.' + linguam.iso6393 +
                        '.typum',
                        fontem=conceptum_sacuum
                    )

                if not valuem:
                    valuem = self._ontologia.de(
                        'terminum.' + linguam.linguam +
                        '.typum',
                        fontem=conceptum_sacuum
                    )

                lineam_1.append(valuem)

            if 'meta' in self.agendum_attributum or \
                    'meta_terminum' in self.agendum_attributum:
                # TODO: this is a draft. need to be implemented
                lineam_1.append("")

        # for item in self.linguam_agendum:
        #     lineam_1.append('')

        # print('conceptum_sacuum', conceptum_sacuum)

        # TODO: the rest of lineam_1

        # TODO: when eventually HXLTM handle better multiline concepts
        #       change here to allow these outputs. For now we're only
        #       already returning List[List] with single line
        resultatum.append(lineam_1)

        return resultatum


class HXLUtilsDeXML:
    """
    HXLUtils contains functions from the Console scripts of libhxl-python
    (HXLStandard/libhxl-python/blob/master/hxl/scripts.py) with few changes
    to be used as class (and have one single place to change).
    Last update on this class was 2021-01-25.

    Author: David Megginson
    License: Public Domain
    """

    def __init__(self):
        """__init__
        """
        # pylint: disable=invalid-name

        self.logger = logging.getLogger(__name__)

        # Posix exit codes
        self.EXIT_OK = 0
        self.EXIT_ERROR = 1
        self.EXIT_SYNTAX = 2

    # def make_args(self, description, hxl_output=True):
    def make_args(self, description, epilog=None, hxl_output=True):
        """Set up parser with default arguments.

        NOTE:
            2021-07-14: Change from libhxl make_args: added epilog option

        @param description: usage description to show
        @param hxl_output: if True (default), include options for HXL output.
        @returns: an argument parser, partly set up.
        """
        # pylint: disable=no-self-use
        if epilog is None:
            parser = argparse.ArgumentParser(description=description)
        else:
            parser = argparse.ArgumentParser(
                description=description,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=epilog
            )
        parser.add_argument(
            'infile',
            help='HXL file to read (if omitted, use standard input).',
            nargs='?'
        )
        if hxl_output:
            parser.add_argument(
                'outfile',
                help='HXL file to write (if omitted, use standard output).',
                nargs='?'
            )

        return parser


if __name__ == "__main__":

    hxltmdexml = HXLTMDeXMLCli()
    args_ = hxltmdexml.make_args()

    hxltmdexml.execute_cli(args_)


def exec_from_console_scripts():
    hxltmdexml_ = HXLTMDeXMLCli()
    args2_ = hxltmdexml_.make_args()

    hxltmdexml_.execute_cli(args2_)
