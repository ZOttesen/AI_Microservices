# Brug en officiel Python image som base
FROM python:3.11-slim

# Sæt working directory inde i containeren
WORKDIR .

# Kopiér requirements.txt og installer afhængigheder
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Kopiér resten af applikationen
COPY . .

# Expose den port som orchestratoren lytter på
EXPOSE 6000

# Sæt miljøvariablerne
ENV PYTHONUNBUFFERED=1

# Start orchestrator-serveren
CMD ["python", "orchestrator.py"]
