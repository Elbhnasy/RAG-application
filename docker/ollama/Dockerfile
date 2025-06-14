FROM ollama/ollama:0.9.1-rc1-rocm

# Install curl for health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the initialization script
COPY ollama/init-ollama.sh /init-ollama.sh

# Set executable permissions
RUN chmod +x /init-ollama.sh

# Set the entrypoint to the script
ENTRYPOINT ["/bin/bash", "/init-ollama.sh"]
