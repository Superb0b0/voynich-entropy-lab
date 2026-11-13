#!/usr/bin/env bash
set -euo pipefail

# Remove tracked Jupyter runtime/configuration files and the known scratch notebook.
# Valid project notebooks under notebooks/ are left untouched.
mode="${1:---dry-run}"
if [[ "$mode" != "--dry-run" && "$mode" != "--apply" ]]; then
  printf 'Usage: %s [--dry-run|--apply]\n' "$0" >&2
  exit 2
fi
git rev-parse --show-toplevel >/dev/null

mapfile -d '' files < <(
  git ls-files -z --     '.jupyter/**'     '.local/share/jupyter/**'     '.jupyter-server-log.txt'     'Untitled.ipynb'     '**/.ipynb_checkpoints/**'
)
if (("${#files[@]}" == 0)); then
  echo "No tracked Jupyter runtime or scratch files found."
  exit 0
fi

printf '%s\n' "Tracked Jupyter artifacts:"
printf '  %s\n' "${files[@]}"
if [[ "$mode" == "--dry-run" ]]; then
  echo "Dry run only. Run with --apply to remove these paths with git rm."
  exit 0
fi
git rm -f -- "${files[@]}"
