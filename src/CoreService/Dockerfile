
FROM python:3.9

RUN pip3 install poetry

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/stock_tracker

WORKDIR /app
COPY . .

RUN poetry config virtualenvs.create false
CMD poetry install && poetry run aerich upgrade && poetry run python coreservice/main.py