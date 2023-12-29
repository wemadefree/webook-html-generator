FROM python:3.8

WORKDIR /app


RUN pip install poetry
RUN POETRY_HOME=/opt/poetry python
RUN poetry config virtualenvs.create false
COPY ./pyproject.toml ./poetry.lock* /app/
RUN poetry install --no-root

COPY . .

RUN apt-get update && apt-get install -y curl gnupg apt-transport-https && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update && apt-get install google-cloud-cli

ENV UPLOAD_DIR=/app/upload
ENV MMG_DIR=/app/mmg

EXPOSE 8000

ENV PYTHONPATH .

CMD ["python", "webook_html_generator/api.py"]