FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 libxslt1.1 curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY *.py ./
COPY templates/ ./templates/

# Build a prebuilt "seed" database at image-build time from the public-domain
# source texts, so a fresh deploy serves scripture with no manual import step.
# The entrypoint copies this into the /data volume whenever the volume is empty.
RUN mkdir -p /seed /tmp/bibles \
    && for f in README.md eng-web.usfx.xml eng-kjv.osis.xml eng-asv.zefania.xml; do \
         curl -fsSL -o "/tmp/bibles/$f" \
           "https://raw.githubusercontent.com/seven1m/open-bibles/master/$f"; \
       done \
    && DATABASE_PATH=/seed/bible.db python3 import_all.py \
         --bibles-dir /tmp/bibles --only eng-web,eng-kjv,eng-asv \
    && rm -rf /tmp/bibles

# Database lives on a named volume mounted at /data; seeded by entrypoint.sh.
ENV DATABASE_PATH=/data/bible.db

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60", "app:app"]
