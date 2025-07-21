# Builder stage: install uv and build dependencies
FROM ghcr.io/astral-sh/uv:0.7.8-python3.11-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Copy only lock and pyproject.toml files to leverage Docker cache
COPY uv.lock pyproject.toml /app/

# Install dependencies only, no project code yet
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy full source code (including main.py)
COPY . /app

# Install project and dependencies (no dev)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Final stage: smaller runtime image
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy installed virtual environment and app code from builder
COPY --from=builder /app /app

# Add virtual environment binaries to PATH
ENV PATH="/app/.venv/bin:$PATH"