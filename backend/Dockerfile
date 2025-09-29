# Use a slim Python base to keep images smaller.
FROM python:3.12-slim

WORKDIR /app

# Leverage Docker layer caching (if requirements don't change,
# this and previous commands aren't re-run).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code.
COPY . .

EXPOSE 8000

# Compose overrides this with --reload in dev, but this is a sensible default.
CMD ["uvicorn", "backend.main:run_app", "--host", "0.0.0.0", "--port", "8000"]
