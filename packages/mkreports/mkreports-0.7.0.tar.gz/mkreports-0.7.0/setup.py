# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mkreports', 'mkreports.md']

package_data = \
{'': ['*'], 'mkreports': ['assets/*']}

install_requires = \
['GitPython>=3.1.26,<4.0.0',
 'PyYAML>=6.0',
 'anytree>=2.8.0,<3.0.0',
 'deepmerge>=0.3.0',
 'immutabledict>=2.2.1',
 'importlib-resources>=5.4.0,<6.0.0',
 'intervaltree>=3.1.0,<4.0.0',
 'mdutils>=1.3.1',
 'mkdocs-material>=7.3.6',
 'mkdocs>=1.2.3',
 'more-itertools>=8.12.0,<9.0.0',
 'parse>=1.19.0,<2.0.0',
 'plotly>=5.5.0,<6.0.0',
 'pytest>=6.2.5',
 'python-frontmatter>=1.0.0',
 'tabulate>=0.8.9',
 'typer>=0.4.0,<0.5.0',
 'typing-extensions<=3.11']

extras_require = \
{':python_version >= "3.7" and python_version < "4.0"': ['mkdocstrings>=0.17.0,<0.18.0']}

setup_kwargs = {
    'name': 'mkreports',
    'version': '0.7.0',
    'description': 'Creating static reports from python using mkdocs',
    'long_description': '![Pytest](https://github.com/hhoeflin/mkreports/actions/workflows/pytest.yml/badge.svg)\n\n# Mkreports package\n\n## Introduction\n\nThe mkreports package makes it easy for you to write complex reports in mkdocs\nincluding tables, graphics and programmatically defined output\nusing only python scripts. No Jupyter notebooks or workarounds such\nas jupytext are needed.\n\nThis methods works seamlessly with complex codebases, encourages\nmodularity and re-useability of code.\n\nBelow is an example of a simple page. However, the documentation for this\npackage is also created with `mkreports`. The code can be found in the\n[documentation](https://hhoeflin.github.io/mkreports/site_code/main/).\n\n## Quickstart\n\nIt is very easy to create new reports and pages. Below an example that\ncreates a report in the `example_report` directory and creates one page\n`quickstart` in which a table and a plot of some data is shown together\nwith the code used to create those items.\n\n```python\nimport pandas as pd\nimport plotnine as p9\nfrom mkreports import Report\nfrom plotnine.data import mtcars\n\nreport = Report.create("example_report", report_name="Mkreports documentations")\n\np = report.page("quickstart")\n\np.H1("Quickstart")\n\np.P(\n    """\n    First, below the code that was used to create this page.\n    It is a very brief example of an page with a table and an image\n    as well as some text, like here.\n    """\n)\n\np.CodeFile(__file__)\n\np.P(\n    """\n    We are quickly analyzing the mtcars dataset\n    that is included with plotnine.\n    """\n)\n\nwith p.H2("Data as a table"):\n\n    p.Tabulator(mtcars, add_header_filters=True, prettify_colnames=True)\n\nwith p.H2("Some simple plots"):\n\n    p.Image(\n        (\n            p9.ggplot(mtcars, p9.aes("wt", "mpg", color="factor(gear)"))\n            + p9.geom_point()\n            + p9.stat_smooth(method="lm")\n            + p9.facet_wrap("~gear")\n        )\n    )\n\n```\n\nNow change to the folder `example_report` and run\n\n```bash\nmkdocs serve\n```\n\nand go to that page. The report will be shown in the browser. As the development\nserver of mkdocs supports automatic reload, as you run code, it will update automatically.\nThis is particularly convenient when running the IPython extension for interactive\nanalyses.\n\n## Why write this package?\n\nIn this reports we want to provide an easier way to create static\nreports for data analysis. The main tool of choice in this space\nare of course Jupyter notebooks which can also be converted to\nstatic html files. So why another tool?\n\nThe main reason is that having to switch to jupyter\nnotebooks breaks a workflow\nin common editors such as vim as they don\'t natively\nsupport jupyter notebooks. This problem can somewhat be\nalleviated by using packages such as `jupytext` that allow\nfor the seamless conversion between notebooks and python files.\nThe end results are ok but not quite satisfactory as\n- One python file corresponds to one output document\n  (which can get very long)\n- Incremental execution is not possible\n- Regular debuggers such as pudb are not supported well supported\n- It does not solve the issue that in remote ssh development\n  shells the viewing of graphics can be complicated\n- The display options for code and complex tables are limited.\n- Easily pass paramters to create reports. This is functionality\n  that for Jupyter is provided by tools such as `papermill`, but\n  can be much easier achieved in native python.\n\nFor this package, the planned features are:\n- Simple and convenient ways to save and include graphics in markdown files\n- Simple way to include tables in markdown files, also for more complicated\n  javascript display options\n- Include code that was run in the output. For this, we would like\n  a tabbed style, so that the code is only visible when desired and not\n  all the time.\n- Include an option to write the local variables of a stacktrace.\n- Use this functionality together with IPython console to get a running\n  log of an analysis session.\n\nUsing the development server of `mkdocs`, live updates of sessions will be\npossible, including live updates of long-running scripts.\n\n## Packages used here\n\n- `mkdocs`: A package to create static websites from markdown documents\n  that provides many features and is the bases for this package.\n- `mkdocs-material`: The material theme for mkdocs that implements\n  some features that we are using.\n- `mdutils`: A package that gives already many options to write out\n  markdown from python and that this package uses internally.\n',
    'author': 'Holger Hoefling',
    'author_email': 'hhoeflin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hhoeflin/mkreports',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
