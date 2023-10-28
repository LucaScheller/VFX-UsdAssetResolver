# Create and source virtual env
python -m venv venv
source venv/bin/activate
# Install dependencies (We can't use the pyproject.toml as it depends on .git)
python -m pip install fastapi[all]