#!/usr/bin/env bash
if [[ -z "${BASH_VERSION:-}" ]]; then
    echo "This script requires bash. Re-running with bash..." >&2
    exec bash "$0" "$@"
fi
set -euo pipefail

IMAGE_NAME=${IMAGE_NAME:-varanusdocker}
XAUTH_FILE=${XAUTHORITY:-/tmp/.docker.xauth}
USE_GUI=${USE_GUI:-1}
USE_GPU=${USE_GPU:-1}

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is not installed or not on PATH." >&2
    exit 1
fi

if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo "Docker image '$IMAGE_NAME' not found. Building it now..."
    docker build -t "$IMAGE_NAME" .
fi

docker_args=(--rm --privileged --net=host -i)

if [[ -t 0 && -t 1 ]]; then
    docker_args+=(-t)
fi

gpu_args=()
if [[ "$USE_GPU" != "0" ]]; then
    runtime_list=$(docker info --format '{{json .Runtimes}}' 2>/dev/null || true)
    if echo "$runtime_list" | grep -q '"nvidia"'; then
        # Prefer the modern --gpus flag when the NVIDIA runtime is available.
        gpu_args+=(--gpus all)
    else
        echo "No NVIDIA runtime detected; continuing without GPU acceleration."
    fi
else
    echo "GPU usage disabled via USE_GPU=0."
fi

cleanup_xhost=false
if [[ "$USE_GUI" != "0" && -n "${DISPLAY:-}" ]]; then
    if command -v xhost >/dev/null 2>&1; then
        if xhost +local:root >/dev/null 2>&1; then
            cleanup_xhost=true
        else
            echo "Warning: could not authorize X server for the container."
        fi
    else
        echo "Warning: xhost not available; GUI apps may not display."
    fi

    if command -v xauth >/dev/null 2>&1; then
        if [[ ! -f "$XAUTH_FILE" ]]; then
            xauth_list=$(xauth nlist "${DISPLAY}" 2>/dev/null | sed -e 's/^..../ffff/' || true)
            if [[ -n "$xauth_list" ]]; then
                echo "$xauth_list" | xauth -f "$XAUTH_FILE" nmerge - >/dev/null 2>&1 || true
            else
                touch "$XAUTH_FILE"
            fi
            chmod a+r "$XAUTH_FILE"
        fi
        docker_args+=(--env "DISPLAY=$DISPLAY" --env "QT_X11_NO_MITSHM=1")
        docker_args+=(--env "XAUTHORITY=$XAUTH_FILE" --volume "$XAUTH_FILE:$XAUTH_FILE")
        docker_args+=(--volume "/tmp/.X11-unix:/tmp/.X11-unix:rw")
    else
        echo "Warning: xauth not available; skipping Xauthority setup."
    fi
else
    echo "DISPLAY not set or GUI disabled; starting container without X11 bindings."
fi

trap 'if $cleanup_xhost; then xhost -local:root >/dev/null 2>&1 || true; fi' EXIT

docker run "${docker_args[@]}" "${gpu_args[@]}" "$IMAGE_NAME"
