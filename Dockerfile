FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# Copy only metadata needed for dependency resolution
COPY pyproject.toml /app/
COPY src /app/src

RUN pip install --no-cache-dir hatch \
    && hatch env create

# Copy app source

ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8501

CMD ["hatch", "run", "webapp"]
