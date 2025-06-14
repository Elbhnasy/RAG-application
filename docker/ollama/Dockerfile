FROM ollama/ollama:0.9.1-rc1-rocm

# Copy the initialization script
COPY ollama/init-ollama.sh /init-ollama.sh

# Set executable permissions
RUN chmod +x /init-ollama.sh

# Set the entrypoint to the script
ENTRYPOINT ["/bin/bash", "/init-ollama.sh"]