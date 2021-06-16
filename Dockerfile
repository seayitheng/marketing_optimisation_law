FROM python:3.8.10-slim-buster

LABEL maintainer="Marketing Optimisation LAW"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# ODBC Drivers
RUN apt-get -y update \
    && apt-get -y install gcc g++

# Install pip requirements
COPY ./src/requirements.txt .
RUN python -m pip install psycopg2-binary
RUN python -m pip install -r requirements.txt
RUN python -m pip install gunicorn
RUN python -m pip install uvicorn

# Install CBC
RUN apt-get install -y -qq coinor-cbc

# Set PythonPath
ENV PYTHONPATH "{PYTHONPATH}:/home/my-law-project-dash/"

# Shift all codes to /app folder, otherwise there are too many folders in root
WORKDIR /home/marketing_optimisation_law/
COPY . /home/marketing_optimisation_law/

# Creates a non-root user and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN useradd appuser && chown -R appuser /home/marketing_optimisation_law/
USER appuser

# Exposing port
EXPOSE 3000

# Command to host app using gunicorn
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "3000", "--workers", "4", "src.api.api_main:app", "--timeout-keep-alive", "300"]

