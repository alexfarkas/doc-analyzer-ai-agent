FROM python:3.14.5-slim-bookworm AS packages-builder

WORKDIR /build

COPY shared/agent-enums /build/shared/agent-enums
COPY shared/db-repository /build/shared/db-repository
COPY shared/rag-client /build/shared/rag-client

RUN pip install --no-cache-dir --upgrade pip build \
    && cd /build/shared/agent-enums && python3 -m build --wheel \
    && cd /build/shared/db-repository && python3 -m build --wheel \
    && cd /build/shared/rag-client && python3 -m build --wheel

FROM python:3.14.5-slim-bookworm AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
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

COPY --from=packages-builder /build/shared/*/dist/*.whl /tmp/wheels/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir /tmp/wheels/*.whl \
    && rm -rf /tmp/wheels

WORKDIR /app/backend

COPY services/doc-analyzer-backend/requirements.txt ./

RUN pip install --no-cache-dir \
    torch==2.12.1 torchvision==0.27.1 torchaudio==2.11.0 \
    --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY services/doc-analyzer-backend ./

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

CMD ["python3", "-m", "src.doc_analyzer_backend.main"]