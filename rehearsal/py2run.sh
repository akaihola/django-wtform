#!/usr/bin/env bash
# Run a Python 2.7 script against an old Django release in a throwaway,
# offline container. Usage: py2run.sh DJANGO_VERSION CODE_DIR SCRIPT [ARGS...]
# SCRIPT is relative to CODE_DIR; CODE_DIR and Django are on PYTHONPATH.
set -euo pipefail
[ $# -ge 3 ] || { sed -n 2,4p "$0" >&2; exit 2; }
version=$1 code=$(realpath "$2") script=$3
shift 3
image=${PY2RUN_IMAGE:-docker.io/library/python:2.7-alpine}
cache=${XDG_CACHE_HOME:-$HOME/.cache}/py2run
src=$cache/Django-$version
if [ ! -d "$src" ]; then
  case $version in
    # PyPI has no files for Django releases before 1.1.4.
    1.0* | 1.1 | 1.1.[0-3]) url=https://www.djangoproject.com/download/$version/tarball/ ;;
    *) url=https://files.pythonhosted.org/packages/source/D/Django/Django-$version.tar.gz ;;
  esac
  mkdir -p "$cache"
  curl -fsSL "$url" | tar xz -C "$cache"
fi
exec podman run --rm --network none \
  -v "$src:/django:ro" -v "$code:/code:ro" -w /code \
  -e PYTHONPATH=/django:/code -e PYTHONDONTWRITEBYTECODE=1 \
  --entrypoint python2 "$image" "$script" "$@"
