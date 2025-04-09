# ✅ Use official Python base image
FROM python:3.9

# ✅ Set working directory
WORKDIR /app

# ✅ Copy backend project files into container
COPY . .

# ✅ Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Expose the port FastAPI runs on
EXPOSE 8000

# ✅ Run FastAPI with auto-reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
