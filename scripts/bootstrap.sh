#!/usr/bin/env sh
set -eu

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Update secrets before deploying."
fi

if [ ! -f configs/restic/restic.env ]; then
  cp configs/restic/restic.env.example configs/restic/restic.env
  echo "Created configs/restic/restic.env. Update backup credentials."
fi

mkdir -p evidence

cat <<MSG
Bootstrap completed.
Next steps:
1) Edit .env and configs/restic/restic.env
2) docker compose pull
3) docker compose up -d
4) ./scripts/validate.sh
MSG
