# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['esparto']

package_data = \
{'': ['*'], 'esparto': ['resources/css/*', 'resources/jinja/*']}

install_requires = \
['beautifulsoup4>=4.7', 'jinja2>=2.10.1', 'markdown>=3.1', 'pyyaml>=5.1']

extras_require = \
{':python_version < "3.7"': ['dataclasses'],
 'extras': ['Pillow>=7.0.0', 'weasyprint>=51']}

setup_kwargs = {
    'name': 'esparto',
    'version': '3.0.2',
    'description': 'Data driven report builder for the PyData ecosystem.',
    'long_description': 'esparto\n=======\n\n[![image](https://img.shields.io/pypi/v/esparto.svg)](https://pypi.python.org/pypi/esparto)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/esparto.svg)](https://pypi.python.org/pypi/esparto/)\n![Build Status](https://github.com/domvwt/esparto/actions/workflows/lint-and-test.yml/badge.svg)\n[![codecov](https://codecov.io/gh/domvwt/esparto/branch/main/graph/badge.svg?token=35J8NZCUYC)](https://codecov.io/gh/domvwt/esparto)\n[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=domvwt_esparto&metric=alert_status)](https://sonarcloud.io/dashboard?id=domvwt_esparto)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/esparto)\n\nIntroduction\n------------\n\n**esparto** is a Python library for building data driven reports with content\nfrom popular analytics packages. The project takes a straightforward approach\nto document design; with a focus on usability, portability, and extensiblity.\n\nCreating a report is as simple as instantiating a Page object and \'adding\' content\nin the form of DataFrames, plots, and markdown text. Documents can be built interactively\nin a notebook environment, and the results shared as a self-contained HTML\npage or PDF file.\n\nFurther customisation of the output is possible by passing a CSS stylesheet,\nchanging the [Jinja](Jinja) template, or declaring additional element styles within\nthe code. The responsive [Bootstrap](Bootstrap) grid ensures documents adapt to\nany viewing device.\n\nBasic Usage\n-----------\n\n```python\nimport esparto as es\n\n# Do some analysis\npandas_dataframe = ...\nplotly_figure = ...\n\n# Create a Page object\npage = es.Page(title="My Report")\n\n# Add content\npage["Data Analysis"]["Plot"] = plotly_figure\npage["Data Analysis"]["Data"] = pandas_dataframe\n\n# Save to HTML or PDF\npage.save_html("my-report.html")\npage.save_pdf("my-report.pdf")\n\n```\n\nMain Features\n-------------\n\n- Interactive document design with Jupyter Notebooks\n- Share as self-contained HTML or PDF\n- Customise with CSS and Jinja\n- Responsive Bootstrap grid layout\n- Content adaptors for:\n    - [Markdown][Markdown]\n    - [Images][Pillow]\n    - [Pandas DataFrames][Pandas]\n    - [Matplotlib][Matplotlib]\n    - [Bokeh][Bokeh]\n    - [Plotly][Plotly]\n\nInstallation\n------------\n\n**esparto** is available from [PyPI][PyPI] and [Conda][Conda]:\n\n```bash\npip install esparto\n```\n\n```bash\nconda install esparto -c conda-forge\n```\n\nDependencies\n------------\n\n- [python](https://python.org/) >= 3.6\n- [jinja2](https://palletsprojects.com/p/jinja/)\n- [markdown](https://python-markdown.github.io/)\n- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)\n- [PyYAML](https://pyyaml.org/)\n\n#### Optional\n\n- [Pillow](https://python-pillow.org/) *(for image content)*\n- [weasyprint](https://weasyprint.org/) *(for PDF output)*\n\nLicense\n-------\n\n[MIT](https://opensource.org/licenses/MIT)\n\nDocumentation\n-------------\n\nDocumentation and examples are available at\n[domvwt.github.io/esparto/](https://domvwt.github.io/esparto/).\n\nContributions, Issues, and Requests\n-----------------------------------\n\nFeedback and contributions are welcome - please raise an issue or pull request\non [GitHub][GitHub].\n\nExamples\n--------\n\nIris Report - [Webpage](https://domvwt.github.io/esparto/examples/iris-report.html) |\n[PDF](https://domvwt.github.io/esparto/examples/iris-report.pdf) | [Notebook](https://github.com/domvwt/esparto/blob/main/docs/examples/iris-report.ipynb)\n\n<br>\n\n<p width=100%>\n<img width=100%  src="https://github.com/domvwt/esparto/blob/1857f1d7411f12c37c96f8f5d60ff7012071851f/docs/images/iris-report-compressed.png?raw=true" alt="example page" style="border-radius:0.5%;">\n</p>\n\n<!-- * Links -->\n[PyPI]: https://pypi.org/project/esparto/\n[Conda]: https://anaconda.org/conda-forge/esparto\n[Bootstrap]: https://getbootstrap.com/\n[Jinja]: https://jinja.palletsprojects.com/\n[Markdown]: https://www.markdownguide.org/\n[Pillow]: https://python-pillow.org/\n[Pandas]: https://pandas.pydata.org/\n[Matplotlib]: https://matplotlib.org/\n[Bokeh]: https://bokeh.org/\n[Plotly]: https://plotly.com/\n[GitHub]: https://github.com/domvwt/esparto\n',
    'author': 'Dominic Thorn',
    'author_email': 'dominic.thorn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://domvwt.github.io/esparto',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1',
}


setup(**setup_kwargs)
