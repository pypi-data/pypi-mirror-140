# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['gbkviz', 'gbkviz.scripts']

package_data = \
{'': ['*'], 'gbkviz': ['genbank/*']}

install_requires = \
['biopython>=1.79,<2.0', 'reportlab>=3.6.2,<4.0.0', 'streamlit>=1.5.0,<2.0.0']

entry_points = \
{'console_scripts': ['download_gbk_from_acc = '
                     'gbkviz.scripts.download_gbk_from_acc:main',
                     'gbkviz_webapp = '
                     'gbkviz.scripts.launch_gbkviz_webapp:main']}

setup_kwargs = {
    'name': 'gbkviz',
    'version': '0.2.1',
    'description': 'Genbank data visualization webapp',
    'long_description': '# GBKviz: Genbank Data Visualization WebApp\n\n[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/moshi4/gbkviz/main/src/gbkviz/gbkviz_webapp.py)\n![Python3](https://img.shields.io/badge/Language-Python3-steelblue)\n![License](https://img.shields.io/badge/License-MIT-steelblue)\n[![Latest PyPI version](https://img.shields.io/pypi/v/gbkviz.svg)](https://pypi.python.org/pypi/gbkviz)  \n\n## Overview\n\nGBKviz is a web-based Genbank data visualization tool developed with streamlit web framework.\nGBKviz allows user to easily and flexibly draw CDSs in specified genomic region (PNG or SVG format is available).\nIt also supports drawing genome comparison results by MUMmer.\nThis software is developed under the strong inspiration of [EasyFig](https://mjsull.github.io/Easyfig/).\n\n![GBKviz Demo GIF](https://raw.githubusercontent.com/moshi4/GBKviz/main/src/gbkviz/gbkviz_demo.gif)  \nClick [here](https://share.streamlit.io/moshi4/gbkviz/main/src/gbkviz/gbkviz_webapp.py) to try GBKviz on Streamlit Cloud.  \n>:warning: Due to the limited resources in Streamlit Cloud, it may be unstable.  \n\n## Install\n\nGBKviz is implemented in Python3 (Tested on Ubuntu20.04)\n\nInstall PyPI stable version with pip:\n\n    pip install gbkviz\n\nIf you want to enable genome comparison in GBKviz, MUMmer is required.  \n\nInstall MUMmer with apt command (Ubuntu):\n\n    sudo apt install mummer\n\n### Dependencies\n\n- [Streamlit](https://streamlit.io/)  \n  Web framework for quick development\n\n- [BioPython](https://github.com/biopython/biopython)  \n  Utility tools for computational molecular biology\n\n- [MUMmer](https://github.com/mummer4/mummer)  \n  Genome alignment tool for comparative genomics\n  \n## Command Usage\n\nLaunch GBKviz in web browser (<http://localhost:8501>):\n\n    gbkviz_webapp\n\n## Genome Comparison\n\nIn GBKviz, genome comparison of uploaded Genbank files is performed by MUMmer.  \nThe following four genome comparison methods are available.\n\n- Nucleotide one-to-one\n- Nucleotide many-to-many\n- Protein one-to-one\n- Protein many-to-many\n\n*one-to-one*: Reciprocal best alignments between reference and query genomes  \n*many-to-many*: One-way best alignments between reference and query genomes  \n\nUser can download and check genome comparison results file.  \nGenome comparison results file is in the following tsv format.  \n\n| Columns      | Contents                                            |\n| ------------ | --------------------------------------------------- |\n| REF_START    | Reference genome alignment start position           |\n| REF_END      | Reference genome alignment end position             |\n| QUERY_START  | Query genome alignment start position               |\n| QUERY_END    | Query genome alignment end position                 |\n| REF_LENGTH   | Reference genome alignment length                   |\n| QUERY_LENGTH | Query genome alignment length                       |\n| IDENTITY     | Reference and query genome alignment identity (%)   |\n| REF_NAME     | Reference genome name tag                           |\n| QUERY_NAME   | Query genome name tag                               |\n',
    'author': 'moshi',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/moshi4/GBKviz/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
