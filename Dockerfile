FROM python:3.13-slim

# prevents python from writing .pyc bytecode files and ensures logs appear immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


WORKDIR /leapscope

COPY pyproject.toml README.md ./
COPY app ./app

RUN python -m pip install --no-cache-dir .
COPY alembic.ini ./
COPY alembic ./alembic


EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]