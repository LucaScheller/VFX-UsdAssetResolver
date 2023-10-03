# Source setup
export REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && (pwd -W 2> /dev/null || pwd))
# Clean existing builds
rm -R ${REPO_ROOT}/docs/book
# Build Python code based on doc strings. This only needs to be done on API changes.
# Generate python venv
# $HFS/python/bin/python -m venv ${REPO_ROOT}/tools/python
# source ${REPO_ROOT}/tools/python/bin/activate
# python -m pip install pydoc-markdown
# This is currently not being used as pydoc-markdown fails to detect all docstrings.
# Build book
mdbook serve --open ${REPO_ROOT}/docs
