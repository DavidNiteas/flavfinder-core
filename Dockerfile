ARG PYTHON_IMAGE=python:3.10-slim
FROM ${PYTHON_IMAGE}

LABEL org.opencontainers.image.title="flavfinder-core"
LABEL org.opencontainers.image.description="Independent, code-only port of the flavfinder MS/MS flavonoid classifier"
LABEL org.opencontainers.image.source="https://github.com/DavidNiteas/flavfinder-core"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

COPY pyproject.toml README.md LICENSE NOTICE AUTHORS CHANGELOG.md CITATION.cff ./
COPY src ./src
COPY configs ./configs
COPY examples ./examples

RUN python -m pip install --no-cache-dir .

ENTRYPOINT ["flavfinder"]
CMD ["--describe"]
