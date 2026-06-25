# Pinned, environment-independent reproduction of the mCytoMAP prior values.
#   docker build -t mcytomap-core .
#   docker run --rm mcytomap-core                          # reproduce + assert every published value
#   docker run --rm mcytomap-core python3 provenance.py --check   # audit committed outputs
#
# The computation uses only the Python standard library and is deterministic, so any
# Python >= 3.10 base yields identical results; 3.12-slim is pinned here for definiteness.
FROM python:3.12-slim

LABEL org.opencontainers.image.title="mcytomap-core" \
      org.opencontainers.image.description="Reference implementation of the mCytoMAP Evidence-Tier prior layer" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/renatosocodato/mcytomap-core"

WORKDIR /app
COPY . /app

# Default: the dependency-free reproduction (exit 0 on success, non-zero on any mismatch).
CMD ["python3", "reproduce_values.py"]
