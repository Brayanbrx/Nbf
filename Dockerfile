FROM python:3.12-slim

# Instalar dependencias del sistema para SQL Server con FreeTDS
RUN apt-get update && apt-get install -y \
    freetds-dev \
    unixodbc-dev \
    unixodbc \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Configurar ODBC para FreeTDS
RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" > /etc/odbcinst.ini

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY . .

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exponer puerto (Render lo redefinirá dinámicamente)
EXPOSE 8000

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production

# Comando por defecto
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
