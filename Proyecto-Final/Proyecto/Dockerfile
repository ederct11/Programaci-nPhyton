# ============================================================================
# Multi-Stage Dockerfile para Worker de Procesamiento de Imágenes
# ============================================================================
#
# Etapa 1: Builder - Instala dependencias y compila paquetes
# Etapa 2: Runtime - Imagen final ligera con solo lo necesario
#

# ============================================================================
# STAGE 1: Builder
# ============================================================================
FROM python:3.11-slim as builder

# Metadatos
LABEL stage=builder

# Variables de entorno para build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /build

# Copiar requirements y crear virtualenv
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

# ============================================================================
# STAGE 2: Runtime
# ============================================================================
FROM python:3.11-slim

# Metadatos
LABEL maintainer="Image Processing Course" \
      version="1.0" \
      description="Worker de procesamiento de imágenes distribuido"

# Variables de entorno para runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    REDIS_DB=0

# Instalar solo librerías runtime necesarias (sin compiladores)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copiar virtualenv desde builder
COPY --from=builder /opt/venv /opt/venv

# Crear directorios de trabajo
WORKDIR /app
RUN mkdir -p /app/images /app/output && \
    chown -R appuser:appuser /app

# Copiar código de la aplicación
COPY --chown=appuser:appuser core/ /app/core/
COPY --chown=appuser:appuser workers/ /app/workers/
COPY --chown=appuser:appuser filters/ /app/filters/

# Cambiar a usuario no-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; r=redis.StrictRedis(host='${REDIS_HOST}', port=${REDIS_PORT}, db=${REDIS_DB}); r.ping()" || exit 1

# Punto de entrada
ENTRYPOINT ["python", "-m", "workers.monitored_redis_worker"]

# Comando por defecto (puede ser sobrescrito)
CMD []



