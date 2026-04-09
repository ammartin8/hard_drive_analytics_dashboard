FROM python:3.13-slim

# Copy uv binary from offcial uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Setting up working directory
WORKDIR /app

# Set virtual environment path
ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency files
COPY pyproject.toml .python-version uv.lock ./

# Install dependencies from lock file
RUN uv sync --locked

# Copy scripts
COPY ./scripts/ingest_data.py .

# Set entrypoint
ENTRYPOINT ["bash"]