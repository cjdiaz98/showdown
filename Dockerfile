FROM pmariglia/gambit-docker as debian-with-gambit

FROM python:3.8-slim

# Copy the gambit binary from the previous stage
COPY --from=debian-with-gambit /usr/local/bin/gambit-enummixed /usr/local/bin

# Set the working directory
WORKDIR /showdown

# Install system-level dependencies (add packages as needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy all local files to the /showdown directory in the container
COPY . /showdown

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir -r requirements-docker.txt

# Set environment variable for Python encoding
ENV PYTHONIOENCODING=utf-8

# Start an interactive shell (bash)
CMD ["/bin/bash"]