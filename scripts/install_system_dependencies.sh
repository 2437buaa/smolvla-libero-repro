#!/usr/bin/env bash
set -euo pipefail

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This helper supports Ubuntu/Debian systems with apt-get." >&2
  exit 1
fi

sudo apt-get update
sudo apt-get install -y \
  git git-lfs ffmpeg build-essential cmake pkg-config \
  libgl1-mesa-dev libosmesa6-dev libglfw3-dev \
  libexpat1 libfontconfig1-dev

git lfs install
echo "System dependencies: OK"

