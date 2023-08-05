# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['convmoji']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['convmoji = convmoji.commit:app']}

setup_kwargs = {
    'name': 'convmoji',
    'version': '0.1.5',
    'description': 'A simple cli tool to commit Conventional Commits with emojis.',
    'long_description': '\n[![Test](https://github.com/KnowKit/convmoji/actions/workflows/test.yaml/badge.svg)](https://github.com/KnowKit/convmoji/actions/workflows/test.yaml)\n[![Codecov](https://codecov.io/gh/KnowKit/convmoji/branch/main/graph/badge.svg?token=84LAM4S1RD)](https://codecov.io/gh/KnowKit/convmoji)\n![PyPI](https://img.shields.io/pypi/v/convmoji?label=convmoji)\n\n# convmoji\n\nA simple cli tool to commit Conventional Commits.\n\n### Requirements\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/convmoji)\n\n### Install\n\n```bash\npip install convmoji\nconvmoji --help\n```\n\n## Examples\n\nA conventianal commit\n````bash\nconvmoji "epic feature added" feat\n````\n\nOne with a scope\n````bash\nconvmoji "epic feature added" feat --scope somescope\n# ✨: epic feature added\n````\n\nWith some options\n````bash\nconvmoji "epic feature added" feat --scope somescope --amend --no-verify\n# ✨(somescope): epic feature added --amend --no-verify\n````\n\nWith more textual information\n````bash\nconvmoji "epic feature added" feat --scope somescope \\\n  --body "more body information" --foot "more footer information"\n# ✨(somescope): epic feature added\n# \n# more body information\n# \n# more footer information\n````\n\nInform people about breaking changes\n````bash\nconvmoji "epic feature added" feat --scope somescope \\\n  --body "more body information" --footer "more footer information" \\\n  --breaking-changes "breaks somthing"\n# ✨‼️(somescope): epic feature added\n# \n# more body information\n# \n# BREAKING CHANGE: breaks somthing\n# more footer information\n````\n\n> If you want to see what to does without performing the action, run it with `--debug`\n\n## Commit types\n\nFor details on commit types see [conventional commits specification](https://www.conventionalcommits.org/en/v1.0.0/#specification).\n\n* `feat`: ✨\n* `fix`: 🐛\n* `docs`: 📚\n* `style`: 💎\n* `refactor`: 🔨\n* `perf`: 🚀\n* `test`: 🚨\n* `build`: 📦\n* `ci`: 👷\n* `chore`: 🔧\n\n## convmoji --help\n\n**Usage**:\n\n```console\n$ convmoji [OPTIONS] DESCRIPTION [COMMIT_TYPE]\n```\n\n**Arguments**:\n\n* `DESCRIPTION`: Commit message, as in \'git commit -m "..."\'  [required]\n* `[COMMIT_TYPE]`: Either of [feat, fix, docs, style, refactor, perf, test, build, ci, chore]  [default: feat]\n\n**Options**:\n\n* `-s, --scope TEXT`: Scope for commit (any string)  [default: ]\n* `-b, --body TEXT`: Body message for commit  [default: ]\n* `-f, --foot TEXT`: Footer message (formatted two blank lines below body)  [default: ]\n* `--breaking-changes, --bc TEXT`: Specially formatted message to show changes might break         previous versions  [default: ]\n* `--amend`: Execute commit with --amend  [default: False]\n* `--no-verify`: Execute commit with --no-verify  [default: False]\n* `--co-authored_by, --co TEXT`: A string of authors formatted like:        --co-authored-by \'<User user@no-reply> \'        --co-authored-by \'<User2 user2@no-reply>\'\n* `--debug`: Debug mode (does not execute commit)  [default: False]\n* `--info`: Prompt convmoji info (does not execute commit)\n* `--version`: Prompt convmoji version (does not execute commit)\n* `--install-completion`: Install completion for the current shell.\n* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.\n* `--help`: Show this message and exit.\n',
    'author': 'arrrrrmin',
    'author_email': 'info@dotarmin.info',
    'maintainer': 'arrrrrmin',
    'maintainer_email': 'info@dotarmin.info',
    'url': 'https://github.com/KnowKit/convmoji',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
