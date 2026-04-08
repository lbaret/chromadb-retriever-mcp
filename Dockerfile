# Stage 1: Build environment
FROM almalinux:10-minimal AS builder

# Installation de Python 3.12, pip et git via microdnf (le gestionnaire de paquets allégé)
RUN microdnf install -y python3.12 python3.12-pip git \
    && microdnf clean all

# Installation de uv
RUN pip3.12 install uv

WORKDIR /app

# Copie des fichiers de dépendances
COPY pyproject.toml README.md ./

# Installation propre des dépendances dans le .venv
RUN uv sync

# Copie exclusive de l'environnement virtuel et du code source
COPY ./src /app/src

# Définition des variables d'environnement
# Important : on s'assure que le .venv est prioritaire dans le PATH
ENV PATH="/app/.venv/bin:$PATH"
# ENV PYTHONPATH="/app:$PYTHONPATH"

# Configuration pour la connexion à la base de données Chroma
ENV CHROMA_HOST="chroma-db"
ENV CHROMA_PORT="8000"

# Exposition du port
EXPOSE 8000

# Lancement du serveur MCP (note: on utilise python3.12 explicitement)
CMD ["python", "-m", "src.server"]
