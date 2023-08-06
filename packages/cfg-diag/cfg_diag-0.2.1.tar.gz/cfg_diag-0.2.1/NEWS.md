# Change log for cfg-diag library

## 0.2.1

- include the .editorconfig file in the sdist tarball

## 0.2.0

- drop Python 3.6 as a supported version, add Python 3.10 instead
- reformat the source code using black 22 and 100 characters per line
- drop the useless basepython definition from the Tox test environments
- add a pytest >= 6 dependency for the mypy environment and drop the type stubs
- reflow the tox.ini file with a four-character indent
- add an EditorConfig definitions file
- add a flake8 + hacking Tox test environment

## 0.1.1

- move some tool configuration options to setup.py and pyproject.toml
- add Python 3.9 as a supported version
- use unittest.mock instead of mock
- fix a code comment
- add a manifest to include more files in the source distribution

## 0.1.0

- first public release
