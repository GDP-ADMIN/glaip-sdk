#!/bin/bash
# shellcheck disable=SC2086,SC2064,SC2155

# Common configuration and utility functions for build scripts
# This file should be sourced in other build scripts
if [[ "$RUNNER_OS" == "macOS" ]]; then
    sed(){
        command gsed -i "$@"
    }
else
    sed(){
        command sed -i "$@"
    }
fi

# Function to configure build files
configure_build_files() {
    local version="$1"
    uv version $version
}

# Function to install system dependencies based on OS
install_system_dependencies() {
    if [ "$RUNNER_OS" == "macOS" ]; then
        # Fixes building 'hnswlib' extension clang: error: unsupported argument 'native' to option '-march='
        # https://github.com/chroma-core/chroma/issues/221#issuecomment-1490362337
        export HNSWLIB_NO_NATIVE=1
        # Fixes macOS stuck at [keyring:keyring.backend] Loading macOS
        # https://github.com/python-poetry/poetry/issues/8623#issuecomment-1920957707
        export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
        brew install libmagic || :
        brew install ccache || :
        brew install gsed || :
        brew install cmake || :
        brew install coreutils || :
        brew install pkg-config || :
        brew install sentencepiece || :
        brew install protobuf || :
        brew install protobuf-c || :
        brew install cairo || :
        export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
        export DYLD_LIBRARY_PATH="/usr/local/lib:/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
    elif [ "$RUNNER_OS" == "Windows" ]; then
        export PYTHONUTF8=1
    else
        apt-get update
        apt-get install -y cmake
    fi
}

# Function to run tests with coverage
run_tests() {
    # TODO: Fix ruff check
    # uv run ruff check
    uv run coverage run -m pytest --cov-report=xml --cov=. tests/ || [[ $? -eq 5 ]]
}

# Function to install Poetry dependencies
install_dependencies() {
    max_retries=3
    count=0
    delay=5

    until uv sync --all-extras; do
    count=$((count + 1))
    if [ $count -ge $max_retries ]; then
        echo "uv sync failed after $count attempts."
        exit 1
    fi

    echo "uv sync failed. Retrying in $delay seconds... ($count/$max_retries)"
    sleep $delay
    done

    echo "uv sync succeeded."
}

# Function to convert package name from kebab-case to snake_case
convert_to_snake_case() {
    local folder_name="$1"
    echo "$folder_name" | tr '-' '_'
}

# Function to convert package name from snake_case to kebab-case
convert_to_kebab_case() {
    local folder_name="$1"
    echo "$folder_name" | tr '_' '-'
}

build() {
    uv build --wheel
}
