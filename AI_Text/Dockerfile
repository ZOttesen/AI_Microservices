FROM python:3.11-slim

# Indstil arbejdsmappe i containeren
WORKDIR /app

# Kopiér projektfiler og requirements.txt
COPY . .
COPY requirements.txt .

# Installer afhængigheder
RUN pip install --no-cache-dir -r requirements.txt

# Eksponer port 7000
EXPOSE 7000

# Start applikationen
CMD ["uvicorn", "openai_chat:app", "--host", "0.0.0.0", "--port", "7000"]
