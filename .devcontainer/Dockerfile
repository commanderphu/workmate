# ===== Base Image: Python + Node für FastAPI & Vue =====
FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# ================================
# 🧰 System-Tools & Essentials
# ================================
RUN apt-get update && apt-get install -y \
    curl git zsh sudo ca-certificates bash gnupg \
    && rm -rf /var/lib/apt/lists/*

# ================================
# 🟢 Node.js + PNPM Setup
# ================================
# Install Node.js (v20 LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g corepack && \
    corepack enable && \
    corepack prepare pnpm@latest --activate

# Verify installations (optional, aber nützlich im Log)
RUN node -v && pnpm -v && python3 --version

# ================================
# 🐍 Python Tools
# ================================
RUN pip install --no-cache-dir black ruff

# ================================
# ⚙️ Arbeitsverzeichnis
# ================================
WORKDIR /workspace

# ================================
# 💤 Container Idle Mode
# ================================
CMD ["sh", "-c", "echo '✅ Devcontainer ready – awaiting VS Code attach' && tail -f /dev/null"]
