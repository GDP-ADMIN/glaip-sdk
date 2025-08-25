#!/bin/bash
set -e

# Check if at least one package folder name is provided
if [ "$#" -le 0 ]; then
  echo "Error: Missing required argument package_name"
  echo "Usage: ./publish.sh <package_name>"
  exit 1
fi

MODULE="$1"
cd "$MODULE"

if [ -n "${TAG_NAME}" ] && [ "${VERSION}" = "3.12" ]; then
  # Publish to PyPI public registry
  uv publish --no-cache
else
  echo "No release tag detected or VERSION is not 3.12. Skipping package upload."
fi
