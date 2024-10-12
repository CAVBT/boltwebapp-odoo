# Use the official Odoo image from Docker Hub
FROM odoo:18.0

# Ensure we're running as root before installing packages
USER root

# Copy your custom addons to the Odoo addons directory
COPY ./addons /mnt/extra-addons

# Install any additional dependencies your addons might need
RUN apt-get update && apt-get install -y \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Fix permissions for Odoo session directory
RUN mkdir -p /var/lib/odoo/sessions \
    && chown -R odoo:odoo /var/lib/odoo/sessions \
    && chmod -R 755 /var/lib/odoo/sessions

# Set ownership for custom addons
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch back to the Odoo user for running the service
USER odoo

# Expose Odoo default port
EXPOSE 8069
