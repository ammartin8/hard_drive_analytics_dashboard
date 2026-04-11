FROM apache/airflow:3.1.8

ENV AIRFLOW_HOME=/opt/airflow

# Copy uv binary from offcial uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/


WORKDIR $AIRFLOW_HOME

# Copy dependency files
COPY ./pyproject.toml ./.python-version ./uv.lock ./

RUN uv venv && uv sync

USER $AIRFLOW_UID