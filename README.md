# AWSSheet Application

Deploy and run the AWSSheet Django application using Podman, a daemonless container engine.

## Prerequisites

- Podman installed on your system (check with `podman --version`)
- For macOS and Windows users, Podman machine support is required

## Setup and Deployment

### Podman Machine

For macOS and Windows:

```bash
podman machine init  # Initialize a new Podman machine
podman machine start # Start the machine
podman build -t awssheet .  # Build the container image
podman run --name awssheet --publish 8000:8000 -d awssheet  # Run the container

Access the application at http://localhost:8000.