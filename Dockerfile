FROM python:3.12-slim AS builder

RUN apt-get update && \
  apt-get install -y --no-install-recommends build-essential libpq-dev && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade setuptools poetry pyopenssl

WORKDIR /app

COPY poetry.lock pyproject.toml ./

COPY . .

RUN poetry config virtualenvs.create false && poetry install --no-root

FROM python:3.12-slim

ARG DOTFILE=.env

RUN apt-get update && \
  apt-get install -y --no-install-recommends libpq5 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY ./config/${DOTFILE} .env
COPY prestart.sh /usr/local/bin/prestart.sh

ENV PYTHONPATH="/app"
EXPOSE 8000

RUN chmod +x /usr/local/bin/prestart.sh

CMD ["/usr/local/bin/prestart.sh"]
