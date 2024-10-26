# Use the latest Ubuntu image
FROM ubuntu:latest

# Set environment variables to avoid user interaction during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    curl \
    git \
    && apt-get clean

# Set Python alias for convenience
RUN ln -s /usr/bin/python3 /usr/local/bin/python

# Create a workspace directory
WORKDIR /workspace

# Set user to non-root for VSCode container compatibility
ARG USERNAME=vscode
RUN useradd -m $USERNAME
USER $USERNAME

# Copy project files (this step depends on your project structure)
# COPY . /workspace/

# By default, run a bash shell
CMD ["bash"]
