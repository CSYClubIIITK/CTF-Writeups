# ───────────────────────────────────────────────────────────────────
# Dockerfile — Harmonix-7 SoC Emulator
# ───────────────────────────────────────────────────────────────────
# Build:   docker build -t harmonix7 .
# Run:     docker run -p 1337:1337 harmonix7
# ───────────────────────────────────────────────────────────────────

FROM python:3.12-slim

# Metadata
LABEL maintainer="Babu-Nambothiri"
LABEL description="UARTs are a pain in the ass"

# Create a non-root user
RUN useradd -m -s /bin/bash harmonix

# Working directory
WORKDIR /challenge

# Copy only what's needed
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py device.py flag_generator.py ./

# Drop privileges
USER harmonix

# Expose the UART TCP port
EXPOSE 1337

# Run the emulator
CMD ["python", "-u", "device.py"]
