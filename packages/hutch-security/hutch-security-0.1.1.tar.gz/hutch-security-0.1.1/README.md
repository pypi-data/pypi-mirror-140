<img src="./docs/images/hutch.png" alt="Hutch" width="450px" />

## Hutch - Security Engineering Toolkit.

This toolkit provides a collection of widgets commonly used by the HashiCorp Security
Engineering team.

Why Hutch? Hutch provides a home for smaller tools which aren't large enough for a home
of their own.

### Documentation

Documentation for this toolkit is provided by Sphinx. As long as docstrings are defined
using [reST](https://en.wikipedia.org/wiki/ReStructuredText), Sphinx will generate API
documentation - including type annotations - directly from modules in this toolkit.

This documentation can be regenerated at any time using `make documentation`.

Please ensure to push code changes and documentation updates as separate commits to
enable reviewers to more easily identify relevant code changes during review.

### Dependencies

All dependencies must be pinned. To simplify this process, new dependencies should be
added to `requirements.txt` and `make requirements` run. This will generate new version
pins for all dependencies.

### Getting Started

To begin developing a new module in this toolkit the following steps should be followed:

1. Clone the repository to your workstation.
2. Create a new virtual environment for use during development.
```
python3 -m venv env
source env/bin/activate
```
3. Install required development dependencies.
```
pip install -e .[tests]
```
