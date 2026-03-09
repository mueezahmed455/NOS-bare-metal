# NeuralOS Dockerfile
# Multi-stage build: nos-base → nos-runtime → nos-full

# =============================================================================
# Stage 1: Base Image
# =============================================================================
FROM archlinux:base-devel AS nos-base

# Update system
RUN pacman -Syu --noconfirm

# Install core packages (24 packages)
RUN pacman -S --noconfirm \
    python python-pip python-numpy python-rich python-psutil \
    sudo bash coreutils util-linux procps-ng iproute2 less \
    man-db which htop neofetch tree git vim nano curl wget jq \
    lz4 zstd openssh shadow systemd \
    && pacman -Scc --noconfirm \
    && rm -rf /var/cache/pacman/pkg/*

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM nos-base AS nos-runtime

# Install Python packages
RUN pip install --break-system-packages \
    prompt_toolkit pydantic msgpack click readline \
    && rm -rf /root/.cache/pip

# Create FHS directories
RUN mkdir -p /etc/nos /var/lib/nos /var/log/nos /var/cache/nos \
    /home/user /usr/lib/nos /usr/lib/systemd/system

# Copy rootfs
COPY rootfs/ /

# Make binaries executable
RUN chmod +x /usr/bin/nos* \
    && chmod +x /usr/lib/nos/test_all.py

# Create groups
RUN groupadd -r nos \
    && groupadd -r nosadmin \
    && useradd -r -g nos -G nosadmin,wheel -s /usr/bin/nos-shell nos

# Create interactive user
RUN useradd -m -g users -G wheel,nos,nosadmin -s /usr/bin/nos-shell user \
    && echo 'user:neurlos' | chpasswd 2>/dev/null || true

# Add nos library to Python path
RUN echo "/usr/lib/nos" > /usr/lib/python3.*/site-packages/nos.pth || true

# =============================================================================
# Stage 3: Full Image
# =============================================================================
FROM nos-runtime AS nos-full

# Copy OS identity
COPY rootfs/etc/os-release /etc/os-release

# Write version info
RUN echo '{"version": "0.1.0", "codename": "Synapse", "build_date": "'$(date -Iseconds)'"}' > /etc/nos/version.json

# Initialize state
RUN python3 -c "import json, time; \
    json.dump({\
        'boot_count': 0, \
        'install_date': time.time(), \
        'node_id': 'primary', \
        'models_trained': 0, \
        'federated_round': 0\
    }, open('/var/lib/nos/state.json', 'w'), indent=2)"

# Initialize packages
RUN echo '{"installed": [], "history": []}' > /var/lib/nos/packages.json

# Set hostname
RUN echo "neurlos" > /etc/hostname

# Configure hosts
RUN echo "127.0.0.1   localhost\n::1         localhost" > /etc/hosts

# Locale config
RUN echo "LANG=en_US.UTF-8" > /etc/locale.conf \
    && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen 2>/dev/null || true

# Timezone
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime

# Issue file
RUN echo "NeuralOS v0.1.0 (Synapse) - AI is the OS" > /etc/issue

# Default environment
ENV PYTHONPATH=/usr/lib/nos
ENV NOS_VERSION=0.1.0
ENV NODE_ID=primary
ENV AUTO_LOGIN=true
ENV DEFAULT_USER=user
ENV TERM=xterm-256color

# Expose ports for federated learning
EXPOSE 7700

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from nos import NeuralNode; n = NeuralNode(); print('OK')" || exit 1

# Entry point
ENTRYPOINT ["/usr/bin/nos-init"]
