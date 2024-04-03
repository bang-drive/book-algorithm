#!/usr/bin/env bash

# reuse container -> 0/1
function reuse {
    CONTAINER="$1"
    status=$(docker inspect --format '{{.State.Status}}' "${CONTAINER}" 2> /dev/null)
    if [ "${status}" = "running" ]; then
        return 0
    fi

    if [ ! -z "${status}" ]; then
        docker rm -f "${CONTAINER}"
    fi
    return 1
}
