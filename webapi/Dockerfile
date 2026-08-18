# Backend image for alpha_strategy_parser.
# Uses micromamba (not pip) specifically because TA-Lib needs its underlying
# C library -- conda-forge ships a prebuilt binary, which is far more
# reliable across platforms than compiling the C library from source in a
# plain python:3.11-slim image.
FROM mambaorg/micromamba:1.5.8-jammy

USER root
WORKDIR /app

# Runtime dependencies only -- no antlr4 runtime needed, the live code path
# is src/simple_parser.py (hand-written), not the ANTLR-generated parser.
RUN micromamba install -y -n base -c conda-forge \
    python=3.11 \
    ta-lib \
    fastapi \
    uvicorn \
    pandas \
    numpy \
    pydantic \
    pyarrow \
    && micromamba clean --all --yes

ENV MAMBA_DOCKERFILE_ACTIVATE=1

COPY src/ /app/src/
COPY webapi/app.py /app/webapi/app.py
# Full real dataset (~4,100 NSE symbols, 351MB) -- bundled directly into the
# image so the container is 100% self-contained; the interviewer needs
# nothing but Docker to see the real universe, not a 6-symbol placeholder.
COPY market_data/ /app/data/

ENV DATA_PARTITIONED_PATH=/app/data
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["micromamba", "run", "-n", "base", "uvicorn", "webapi.app:app", \
     "--app-dir", "/app", "--host", "0.0.0.0", "--port", "8000"]
