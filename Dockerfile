# Use the official Python slim base image
FROM python:3.11-slim

# Install  system dependencies for Manim, Automata-lib, LaTeX, and FFmpeg
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libcairo2-dev \
    libpango1.0-dev \
    wget \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Manim and Automata-lib directly using pip
RUN pip install manim automata-lib

# Copy the project files into the container
WORKDIR /app
COPY . /app

# Set up a non-root user to run the application 
ARG NB_USER=appuser
ARG NB_UID=1000
RUN adduser --disabled-password --gecos "User" --uid ${NB_UID} ${NB_USER}

# Ensure that the user has permissions to write to the necessary directories
RUN mkdir -p /app/media && \
    chown -R ${NB_USER}:${NB_USER} /app/media && \
    chmod -R 777 /app/media

USER ${NB_USER}

# Set the default command to run a shell
CMD ["/bin/bash"]
