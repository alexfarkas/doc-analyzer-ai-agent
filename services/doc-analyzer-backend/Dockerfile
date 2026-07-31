FROM python:3.14.5-slim-bookworm AS packages-builder

WORKDIR /build

COPY shared/agent-enums /build/shared/agent-enums
COPY shared/db-repository /build/shared/db-repository
COPY shared/rag-client /build/shared/rag-client

RUN pip install --no-cache-dir --upgrade pip build \
    && cd /build/shared/agent-enums && python -m build --wheel \
    && cd /build/shared/db-repository && python -m build --wheel \
    && cd /build/shared/rag-client && python -m build --wheel

FROM python:3.14.5-slim-bookworm AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser \
    && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY --from=packages-builder /build/shared/agent-enums/dist/*.whl /tmp/wheels/
COPY --from=packages-builder /build/shared/db-repository/dist/*.whl /tmp/wheels/
COPY --from=packages-builder /build/shared/rag-client/dist/*.whl /tmp/wheels/

RUN pip install --no-cache-dir \
    /tmp/wheels/agent_enums-*.whl \
    /tmp/wheels/db_repository-*.whl \
    /tmp/wheels/rag_client-*.whl \
    && rm -rf /tmp/wheels

COPY services/doc-analyzer-backend /app/backend

WORKDIR /app/backend

COPY services/doc-analyzer-backend/requirements.txt /app/backend/requirements.txt

RUN pip install --no-cache-dir \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/documents /app/logs \
    && chown -R appuser:appuser /app

USER appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "api.api:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--timeout-keep-alive", "300", \
     "--timeout-graceful-shutdown", "300"]