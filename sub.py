import subprocess

# Start Streamlit app
streamlit_process = subprocess.Popen(["streamlit", "run", "main2.py"])

# Start FastAPI app
fastapi_process = subprocess.Popen(["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"])

# Wait for both to complete
streamlit_process.wait()
fastapi_process.wait()
