REM Create and source virtual env
python -m venv venv
call venv\Scripts\activate.bat
REM Install dependencies (We can't use the pyproject.toml as it depends on .git)
python -m pip install fastapi[all]