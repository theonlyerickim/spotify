# Base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy files
COPY app.py /app
COPY requirements.txt /app
COPY models /app/models
COPY request /app/request
COPY inference /app/inference
COPY training /app/training
COPY data /app/data

# Install dependencies
RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_lg

# Run the application
EXPOSE 8000
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "--timeout", "120"]
CMD ["app:app"]
