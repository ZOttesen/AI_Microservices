FROM python:3.11-slim

# Arbejdsmappe
WORKDIR /app

# Kopiér krav og installer dem
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiér resten af appen
COPY . .

# Opret output-mappen til lydfiler
RUN mkdir -p audio_files

# Eksponér port 7001
EXPOSE 7001

# Start appen
CMD ["uvicorn", "eleven_labs:app", "--host", "0.0.0.0", "--port", "7001"]
