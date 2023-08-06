# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyfltr']

package_data = \
{'': ['*']}

install_requires = \
['black',
 'flake8-bugbear',
 'isort',
 'joblib',
 'mypy',
 'pylint',
 'pyproject-flake8',
 'pytest',
 'pyupgrade',
 'tomli']

entry_points = \
{'console_scripts': ['pyfltr = pyfltr.pyfltr:main']}

setup_kwargs = {
    'name': 'pyfltr',
    'version': '0.2.0',
    'description': 'pyfltr: Python Formatters, Linters, and Testers Runner.',
    'long_description': '# pyfltr: Python Formatters, Linters, and Testers Runner.\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Lint&Test](https://github.com/ak110/pyfltr/actions/workflows/python-app.yml/badge.svg)](https://github.com/ak110/pyfltr/actions/workflows/python-app.yml)\n[![PyPI version](https://badge.fury.io/py/pyfltr.svg)](https://badge.fury.io/py/pyfltr)\n\nPythonの各種ツールをまとめて呼び出すツール。\n\n- Formatters\n    - pyupgrade\n    - isort\n    - black\n- Linters\n    - pflake8\n    - mypy\n    - pylint\n- Testers\n    - pytest\n\n## 動作詳細\n\n- pytestの対象ファイルは`*_test.py`、pytest以外の対象ファイルは`*.py`\n- 終了コード:\n    - 0: Formattersによるファイル変更無し、かつLinters/Testersでのエラー無し\n    - 1: 上記以外\n\n## コンセプト\n\n- 各種ツールをまとめて呼び出したい\n- 各種ツールのバージョンにはできるだけ依存したくない (ので設定とかは面倒見ない)\n- exclude周りは各種ツールで設定方法がバラバラなのでできるだけまとめて解消したい (のでpyfltr側で解決してツールに渡す)\n- blackやisortはファイルを修正しつつエラーにもしたい (CIとかを想定) (pyupgradeはもともとそういう動作)\n- Q: pysenでいいのでは？ A: それはそう。\n\n## 主な使い方\n\n### 通常\n\n```text\n$ pyfltr [files and/or directories ...]\n```\n\n対象を指定しなければカレントディレクトリを指定したのと同じ扱い。\n\n`*.py`などを指定した場合も、pytestは`*_test.py`に対してのみ実行される。\n\n### 特定のツールのみ実行\n\n```text\n$ pyfltr --commands=pyupgrade,isort,black,pflake8,mypy,pylint,pytest [files and/or directories ...]\n```\n\nカンマ区切りで実行するツールだけ指定する。\n\n## 設定\n\n`pyproject.toml`で設定する。\n\n### 例\n\n```toml\n[tool.pyfltr]\npyupgrade_args = ["--py38-plus"]\npylint_args = ["--jobs=4"]\nextend-exclude = ["foo", "bar.py"]\n```\n\n### 設定項目\n\n設定項目と既定値は`pyfltr --generate-config`で確認可能。\n\n- {command} : コマンドの有効/無効\n- {command}_path : 実行するコマンド\n- {command}_args : 追加のコマンドライン引数\n- exclude : 除外するファイル名パターン(既定値あり)\n- extend-exclude : 除外するファイル名パターン(既定値は空)\n\n## 各種設定例\n\n### pyproject.toml\n\n```toml\n...\n\n[tool.poetry.dev-dependencies]\npyfltr = "*"\n\n[tool.pyfltr]\npyupgrade_args = ["--py38-plus"]\npylint_args = ["--jobs=4"]\n\n...\n```\n\n### .pre-commit-config.yaml\n\n```yaml\n  - repo: local\n    hooks:\n      - id: system\n        name: pyfltr\n        entry: poetry run pyfltr --commands=pyupgrade,isort,black,pflake8\n        types: [python]\n        require_serial: true\n        language: system\n```\n\n### CI例\n\n```yaml\n  - poetry install --no-interaction\n  - poetry run pyfltr\n```\n',
    'author': 'aki.',
    'author_email': 'mark@aur.ll.to',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ak110/pyfltr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
