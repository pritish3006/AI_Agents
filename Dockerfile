# Build stage
FROM continuumio/miniconda3:latest AS builder

# Set working directory
WORKDIR /build

# Copy only environment file first for better caching
COPY environment.yml .

# Create conda environment
RUN conda env create -f environment.yml && \
    conda clean -afy

# Runtime stage
FROM continuumio/miniconda3:latest AS runtime

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -s /bin/bash -d /home/appuser appuser && \
    mkdir -p /home/appuser && \
    chown -R appuser:appuser /home/appuser

# Set working directory
WORKDIR /api

# Copy conda environment from builder
COPY --from=builder /opt/conda/envs/genai_agents /opt/conda/envs/genai_agents

# Initialize conda in bash
RUN conda init bash && \
    echo "conda activate genai_agents" >> ~/.bashrc

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "genai_agents", "/bin/bash", "-c"]

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PYTHONPATH=/api \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/conda/envs/genai_agents/bin:$PATH"

# Switch to non-root user
USER appuser

# Create necessary directories with proper permissions
RUN mkdir -p /home/appuser/.cache && \
    chmod -R 755 /home/appuser/.cache

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["conda", "run", "-n", "genai_agents", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 