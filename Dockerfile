FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    AGENTIC_BOOK_CONTENT_ROOT=/app/content \
    AGENTIC_BOOK_DATA_DIR=/data \
    AGENTIC_BOOK_AUTO_INGEST=true

WORKDIR /app

RUN addgroup --system agentic-book && adduser --system --ingroup agentic-book agentic-book

COPY pyproject.toml README.md ./
COPY src ./src
COPY content ./content
COPY evals ./evals
COPY docker/entrypoint.sh /usr/local/bin/agentic-book-entrypoint

RUN python -m pip install --root-user-action=ignore ".[mcp]" \
    && chmod +x /usr/local/bin/agentic-book-entrypoint \
    && mkdir -p /data \
    && chown -R agentic-book:agentic-book /app /data

USER agentic-book
EXPOSE 8000
VOLUME ["/data"]

ENTRYPOINT ["agentic-book-entrypoint"]
CMD ["agentic-book", "--content-root", "/app/content", "--data-dir", "/data", "serve-mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "8000"]
