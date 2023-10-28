# Create virtual environment
python3 -m venv venv
source venv/bin/activate
python -m pip install -e ../arHttp
uvicorn arHttpSampleServer:app --reload