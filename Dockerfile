# Use an official Python runtime as a parent image
FROM debian:bullseye-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

# Install system dependencies
# This is a more efficient way of installing packages, which also cleans up the apt cache to reduce image size.
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip \
    wget \
    vim \
    git \
    pip \   
    procps \ 
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# You can remove the commented out `pip install` commands if they are included in your requirements.txt



# Make port 8000 available to the world outside this container
EXPOSE 8000

# # Install steamline
# add a non-root 'steampipe' user
RUN adduser --system --disabled-login --ingroup 0 --gecos "steampipe user" --shell /bin/false --uid 9193 steampipe

RUN apt update 
# &&  apt upgrade

# Install terraform
# Install Terraform
# The specific version can be replaced with the desired version of Terraform
ENV TERRAFORM_VERSION=1.5.0
RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip -d /usr/local/bin \
    && rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

# Install Terraform's companion tool, Terraformerr
ENV PROVIDER=all
ENV TERRAFORMER_VERSION=0.8.24

RUN FILENAME="terraformer-${PROVIDER}-linux-amd64" \
    && curl -LO "https://github.com/GoogleCloudPlatform/terraformer/releases/download/$(curl -s https://api.github.com/repos/GoogleCloudPlatform/terraformer/releases/latest | grep tag_name | cut -d '"' -f 4)/${FILENAME}" \
    && chmod +x ${FILENAME} \
    && mv ${FILENAME} /usr/local/bin/terraformer


# Print the installed versions for verification
RUN terraform --version && terraformer --version



RUN /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)"
# Change user to non-root
USER steampipe:0
# In the following commands, the Terraform providers are installed in the /tmp/terraformer directory.
RUN mkdir -p /tmp/terraformer/aws /tmp/terraformer/gcp /tmp/terraformer/azure

# Copy the current directory contents into the container at the work directory
# Assuming that the Docker build context is set to the project root directory (where manage.py is located)
COPY --chown=steampipe awssheet/ .
# Install Steampipe plugins
RUN steampipe plugin install steampipe 
RUN steampipe plugin install aws 
RUN git clone https://github.com/turbot/steampipe-mod-aws-compliance.git /tmp/steampipe-mod-aws-compliance

RUN steampipe plugin install gcp
RUN git clone https://github.com/turbot/steampipe-mod-gcp-compliance.git /tmp/steampipe-mod-gcp-compliance

RUN steampipe plugin install azure
RUN git clone https://github.com/turbot/steampipe-mod-azure-compliance.git /tmp/steampipe-mod-azure-compliance

RUN steampipe plugin install kubernetes
ENV STEAMPIPE_CACHE=true
ENV STEAMPIPE_MEMORY_MAX_MB=0
ENV STEAMPIPE_MAX_PARALLEL=20
# Set a soft memory limit for the steampipe process.
ENV STEAMPIPE_MEMORY_MAX_MB=2048
ENV STEAMPIPE_PLUGIN_MEMORY_MAX_MB=2048
# ENV STEAMPIPE_PLUGIN_MEMORY_MAX_MB=2
# The maximum amount of time to cache results, in seconds.
ENV STEAMPIPE_CACHE_MAX_TTL=3000
# The amount of time to cache results, in seconds.
ENV STEAMPIPE_CACHE_TTL=3000 

COPY start.sh /start.sh
CMD ["/start.sh"]

# CMD steampipe service start

# # Collect static files
# # Uncomment this if you are collecting static files in your Django project
# # RUN python3 manage.py collectstatic --noinput

# # Start your Django application
# # There can only be one CMD instruction in a Dockerfile. If you list more than one, only the last CMD will take effect.
# # CMD python3 manage.py migrate sessions &&
# CMD python3 manage.py runserver 0.0.0.0:8000
