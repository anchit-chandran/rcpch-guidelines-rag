FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# System dependencies for `unstructured` to parse PDFs, Word, HTML, etc.
RUN apt-get update && apt-get install -y \
	libmagic-dev \
	poppler-utils \
	tesseract-ocr \
	qpdf \
	libreoffice \
	pandoc

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN uv sync --locked

# Default entrypoint (to be updated with actual script)
CMD ["uv", "python", "main.py"]
